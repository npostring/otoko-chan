import subprocess
import pretty_midi
from pychord import Chord


class OtokoChanCore(object):
    def __init__(self):
        pass

    # テキストからMIDIに変換する
    def create_text_to_midi(self, chords: str, midi: str, instrument: str = 'Acoustic Grand Piano'):
        # chordsは下記のような文字列
        # FM7 G7 Em7 Am7

        # 改行・コマンド・スペースを削除
        chords = chords.replace('\n', ' ')
        chords = chords.replace('　', ' ')
        chords = chords.split(' ')
        chords = list(filter(None, chords))

        # ディグリーをハ長調基準でアルファベットに変換
        temp_alphabet_roots = ['c', 'd', 'e', 'f', 'g', 'a', 'b']
        temp_degree_roots = ['ⅰ', 'ⅱ', 'ⅲ', 'ⅳ', 'ⅴ', 'ⅵ', 'ⅶ']
        for kk in range(len(chords)):
            for ii in range(len(temp_degree_roots)):
                chords[kk] = chords[kk].replace(temp_degree_roots[ii], temp_alphabet_roots[ii])

        # 未対応のコードを補足
        chords_instance = []
        error_chords = []
        for chord in chords:
            try:
                chords_instance.append(Chord(chord))
            except ValueError:
                error_chords.append(chord)
        if len(error_chords) != 0:
            raise ValueError(error_chords)
        chords = chords_instance

        # コードをMIDIとして追加
        midi_data = pretty_midi.PrettyMIDI()
        piano_program = pretty_midi.instrument_name_to_program(instrument)
        piano = pretty_midi.Instrument(program=piano_program)
        length = 1
        for n, chord in enumerate(chords):
            for note_name in chord.components_with_pitch(root_pitch=4):
                note_number = pretty_midi.note_name_to_number(note_name)
                note = pretty_midi.Note(velocity=100, pitch=note_number, start=n * length, end=(n + 1) * length)
                piano.notes.append(note)
        midi_data.instruments.append(piano)

        midi_data.write(midi)

    # MIDIから音声に変換する
    def create_midi_to_mp3(self, soundfont: str, midi: str, audio: str):
        subprocess.run(
            ['fluidsynth', '-ni', '-g', str(1.0), soundfont, midi, '-F', audio, '-r', str(44100)],
        )

        subprocess.run(
            ['lame', '-b', str(192), audio]
        )
