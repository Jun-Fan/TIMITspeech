import numpy as np
import scipy.io.wavfile as wav

from helpFunctions.copyFilesOfType import *
from transform import *


def main():
    nbPhonemes = 39
    ############### DATA LOCATIONS  ###################
    FRAC_VAL = 0.1  # fraction of training data to be used for validation
    root = os.path.expanduser("~/TCDTIMIT/audioSR/")  # ( keep the trailing slash)

    # dataset = "TIMIT"
    dataset = "TCDTIMIT"  # eg TIMIT. You can also manually split up TCDTIMIT according to train/test split in Harte, N.; Gillen, E., "TCD-TIMIT: An Audio-Visual Corpus of Continuous Speech," doi: 10.1109/TMM.2015.2407694

    dataRootDir = root + dataset + "/fixed" + str(nbPhonemes) + os.sep + dataset
    source = os.path.join(dataRootDir, 'TEST')
    # source = os.path.join(dataRootDir, 'lipspeakers')

    print("src: " + source)

    noiseTypes = ['voices', 'white']
    ratio_dBs = [0, -3, -3, -5, -10]
    for noiseType in noiseTypes:
        for ratio_dB in ratio_dBs:
            test_dst = root + dataset + "/fixed" + str(nbPhonemes) + "_" + noiseType + os.sep + "ratio" + str(
                ratio_dB) + os.sep + os.path.basename(source)
            print("dest: " + test_dst)
            # import pdb;pdb.set_trace()
            generateBadAudio(noiseType, source, test_dst, ratio_dB)


# from scikits.audiolab import wavread, wavwrite
from pydub import AudioSegment


# merge wav1 and wav2 to out, ratio wav1/wav2 in out is ratio (ratio given in dB)
def mergeAudioFiles(wav1_path, wav2_path, out_path, ratio_dB):
    # https://github.com/jiaaro/pydub/b

    sound1 = AudioSegment.from_file(wav1_path);
    loud1 = sound1.rms
    sound2 = AudioSegment.from_file(wav2_path);
    loud2 = sound2.rms

    targetRMS = (sound1 + ratio_dB).rms

    # bring them to approx equal volume + ratio_dB
    min_acc = 5
    while sound2.rms < targetRMS - min_acc:
        sound2 += min_acc / 20.0  # this changes in dB, but we're looking at the RMS result -> /20
    while sound2.rms > targetRMS + min_acc:
        sound2 -= min_acc / 20.0

    # print(sound1.rms, targetRMS, sound2.rms)

    combined = sound1.overlay(sound2, loop=True)

    combined.export(out_path, format='wav')


def generateBadAudio(outType, srcDir, dstDir, ratio_dB):
    # copy phoneme files
    copyFilesOfType(srcDir, dstDir, ".phn")

    # copy merged wav files
    noiseFile = createNoiseFile(ratio_dB)
    src_wavs = loadWavs(srcDir)
    for i in tqdm(range(len(src_wavs))):
        relSrcPath = relpath(srcDir, src_wavs[i]).lstrip("../")
        # print(relSrcPath)
        destPath = os.path.join(dstDir, relSrcPath)
        if outType == 'voices':
            # index of voice to merge
            j = random.randint(0, len(src_wavs) - 1)
            mergeAudioFiles(src_wavs[i], src_wavs[j], destPath, ratio_dB)
        else:
            mergeAudioFiles(src_wavs[i], noiseFile, destPath, ratio_dB)


import random


def createNoiseFile(ratio_dB, noise_path='noise.wav'):
    rate = 16000
    noise = np.random.normal(0, 1, rate * 3)  # generate 3 seconds of white noise
    wav.write(noise_path, rate, noise)

    # change the volume to be ~ the TIMIT volume
    sound = AudioSegment.from_file(noise_path);
    loud2 = sound.dBFS
    while sound.dBFS > -30 + ratio_dB:
        sound -= 1

    sound.export(noise_path, format='wav')
    return os.path.abspath(noise_path)


if __name__ == "__main__":
    main()
