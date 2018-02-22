import os
import subprocess
import chardet
import concurrent.futures
import sys

nrThreads = 3
logger = logging.getLogger()


def worker(item):
    print(F"Item: {item}")
    spl = item.split("\\")
    path = spl[0] + "\\"
    for i in spl[1:-1]:
        path = os.path.join(path, i)

    print(F"Pfad: {path}")
    basename = spl[-1:][0][:-5]
    # print(basename)
    newBasename = os.path.join(path, basename+".flac")

    command = ["opusenc.exe", "--bitrate", "256", newBasename,
               os.path.join(path, basename + ".opus")]
    p = subprocess.Popen(command)
    p.wait()
    
    if os.path.exists(newBasename):
        if os.stat(newBasename).st_size <= 0:
            logging.error("Error: {} size <=0".format(newBasename))
        else:
            os.remove(newBasename)
    else:
        logging.error("Error: {} does not exist".format(newBasename))


def renameFlacToOpus():
    for root, dirs, files in os.walk(os.getcwd()):
        for file in files:
            if file.endswith(".cue"):
                out = []
                encoding = chardet.detect(open(os.path.join(root, file), "rb").read())
                with open(os.path.join(root, file), "rb") as f:
                    print(os.path.join(root, file))

                    lines = f.readlines()
                    for l in lines:
                        l = l.decode(encoding.get("encoding"))
                        l = l.replace(".flac", ".opus")
                        l = l.replace(".wav", ".opus")
                        out.append(l)
                with open(os.path.join(root, file), "wb") as f:
                    for o in out:
                        f.write(o.encode("utf-8"))


def processFlacs():
    s = set()
    for root, dirs, files in os.walk(os.getcwd()):
        for file in files:
            if file.endswith(".flac"):
                basename = file[:-5]
                if not os.path.exists(os.path.join(root, basename + ".opus")):
                    s.add(os.path.join(root, file))
            if file.endswith(".wav"):
                basename = file[:-4]
                if not os.path.exists(os.path.join(root, basename + ".opus")):
                    s.add(os.path.join(root, file))

    executor = concurrent.futures.ThreadPoolExecutor(max_workers=nrThreads)
    for i in s:
        executor.submit(worker, i)
    executor.shutdown()


# geenerate cuefiles if none are present
def generateCues(root, musicfiles):
    cuelines = []
    cuelines.append("REM GENRE CLASSICAL")
    cuelines.append("REM COMMENT \"Created with OpusEncoder\"")
    dirname = root[root.rfind("\\") + 1:]
    cuelines.append(F"TITLE \"{dirname}\"")
    counter = 1
    for m in musicfiles:
        cuelines.append(F"FILE \"{m}\" WAVE")
        track = "0" + str(counter) if counter < 10 else counter
        cuelines.append(F"\tTRACK {track} AUDIO")
        cuelines.append(F"\t\tTITLE \"{m}\"")
        cuelines.append("\t\tINDEX 01 00:00:00")
        counter += 1

    with open(os.path.join(root, dirname + ".cue"), "w") as out:
        for line in cuelines:
            out.write(line + "\n")


def processCues(root, musicfiles, cuefiles):
    pass


def generateCueFiles():
    for root, dirs, files in os.walk(os.getcwd()):
        musicfiles = []
        cuefiles = []
        for file in files:
            if file.endswith(".ogg") or file.endswith(".opus") or file.endswith(".ape") or file.endswith(".mp3"):
                musicfiles.append(file)
            if file.endswith(".cue"):
                cuefiles.append(file)

        if len(musicfiles) > 0:
            if len(cuefiles) > 0:
                processCues(root, musicfiles, cuefiles)
            else:
                generateCues(root, musicfiles)


def main():
    error_handler = logging.FileHandler("errorlog.txt")
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(logging.Formatter("%(asctime)-15s %(levelname)s %(message)s"))

    # Handler to log messages to file
    log_handler = logging.FileHandler("log.txt")
    log_handler.setLevel(logging.INFO)
    log_handler.setFormatter(logging.Formatter("%(asctime)-15s %(levelname)s %(message)s"))

    # Handler for loging to stdout
    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setLevel(logging.INFO)
    stdout_handler.setFormatter(logging.Formatter("%(message)s"))

    logging.basicConfig(level=logging.DEBUG, handlers=[error_handler,
                                                       log_handler,
                                                       stdout_handler])
    processFlacs()
    renameFlacToOpus()
    generateCueFiles()


if __name__ == "__main__":
    main()
