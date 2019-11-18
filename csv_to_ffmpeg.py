# start with csv as a list
import csv
import argparse

def configure():
    description = 'Convert .csv to .txt for use with ffmpeg -f concat'
    parser = argparse.ArgumentParser(description)
    parser.add_argument('input', metavar='\b', type=str, nargs='?', default=None)
    parser.add_argument('-o', '--output', metavar='\b', type=str, help='Output file to write ffmpeg timestamps to')
    parser.add_argument('-f', '--fuzz', metavar='\b', type=int, help='Amoutn of fuzz to add to each end of timestamps')
    args = parser.parse_args()
    return args


class Timestamp:
    """converts from timestamp to seconds, also holds description"""

    def __init__(self, file, start, stop, description):
        self.file = file
        self.start = start
        self.stop = stop
        self.description = description
        self.fuzz = 0

    @classmethod
    def from_row(cls, row):
        file, start, stop, description = row  # unpacking
        return cls(file, start, stop, description)

    def _to_seconds(self, ts: str) -> int:
        """Convert from MM:SS or HH:MM:SS format to number of seconds"""
        ts_format = {
            (4, 5): '%M:%S',
            (7, 8): '%H:%M:%S'
        }
        if len(ts) in (4, 5):
            m, s = ts.split(':')
            m = int(m) * 60
            s = int(s)
            return (m + s)
        elif len(ts) in (7, 8):
            h, m, s = ts.split(':')
            h = int(h) * 3600
            m = int(m) * 60
            s = int(s)
            return (h + m + s)

    @property
    def start_secs(self):
        start = self._to_seconds(self.start) - self.fuzz
        return start

    @property
    def stop_secs(self):
        stop = self._to_seconds(self.stop) + self.fuzz
        return stop

    def format_for_concat(self):
        out_str = f"file {self.file}\ninpoint {self.start_secs}\noutpoint {self.stop_secs}\n"
        return(out_str)


def read_file(filename, fuzz):
    with open(filename, newline='') as csvfile:
        ts_list = []
        tsreader = csv.reader(csvfile)
        next(tsreader)  # skip the header lines
        for row in tsreader:
            # fill filenames downwards
            if ts_list and not row[0]:
                row[0] = ts_list[-1].file
            ts = Timestamp.from_row(row)
            ts.fuzz = fuzz
            ts_list.append(ts)
    return ts_list


def write_txt(filename, ts_list):
    with open(filename, 'w') as f:
        for ts in ts_list:
            f.write(ts.format_for_concat())


if __name__ == '__main__':
    args = configure()
    ts_list = read_file(filename=args.input, fuzz=args.fuzz)
    write_txt(filename=args.output, ts_list=ts_list)



