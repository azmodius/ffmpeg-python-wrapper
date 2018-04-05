import os
import sys
import shlex
import fnmatch
import argparse
import subprocess

def concat(args):

  if args.input is not None:
    file_list = args.input
  else:
    file_list = get_files_in_directory(args.directory, ".MP4")

  if args.input is not None:
    check_list_of_files(file_list)

  if args.directory is not None and not os.path.exists(args.directory):
    print('directory doesnt exist')
    return

  output_path = args.output
  output_dir = os.path.dirname(output_path)
  try:
      os.stat(output_dir)
  except:
      os.mkdir(output_dir)

  if(args.lossless):
    temp_list = []
    for file in file_list:
        file_name_ts = '{file_name}.ts'.format(output_dir=output_dir, file_name=file)
        temp_list.append(file_name_ts)
        temp_command = '{ffmpeg} -i {file_name} -c copy -bsf:v h264_mp4toannexb -f mpegts {filets} -y'.format(ffmpeg=args.ffmpeg_path,
                                                                                                    file_name=file,
                                                                                                    filets=file_name_ts)
        print('running {0}'.format(temp_command))
        os.system(temp_command)

    concat_string = 'concat:{0}'.format('|'.join(temp_list))
    command = '{ffmpeg} -i "{concat}" -c copy -bsf:a aac_adtstoasc {output_path} -y'.format(ffmpeg=args.ffmpeg_path,
                                                                                        concat=concat_string,
                                                                                        output_path=output_path)
  else:
    concat_string = 'concat:{0}'.format('|'.join(args.input))
    command = '{ffmpeg} -i "{concat}" -c copy {output_path}'.format(concat=concat_string,
                                                                    output_path=output_path,
                                                                    ffmpeg=args.ffmpeg_path)

  print('running {0}'.format(command))
  exit_code = os.system(command)

  print(exit_code)

def check_list_of_files(files):
  for file in files:
    if not os.path.isfile(file):
      print('file {file} does not exist.'.format(file))
      return False
  return True

def get_files_in_directory(directory, extension):
    files = [os.path.abspath(os.path.join(directory, f)) for f in os.listdir(directory) if f.endswith(extension)]
    files.sort()
    return files

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()

    parser_concat = subparsers.add_parser("concat", help="Concat list of files")
    concat_group = parser_concat.add_mutually_exclusive_group()
    concat_group.add_argument("-i", 
                              "--input",
                              nargs='+',
                              help="files to concat")
    concat_group.add_argument("-d", 
                              "--directory",
                              type=str,
                              help="files to concat")
    parser_concat.add_argument("-o", "--output",
                                help="concatted file path",
                                required=True)
    parser_concat.add_argument("--ffmpeg-path",
                                default="ffmpeg",
                                help="path to ffmpeg")
    parser_concat.add_argument("-l", "--lossless",
                                action='store_true',
                                help="lossless command")
    parser_concat.add_argument("--delete-sources",
                                action='store_true',
                                help="delete original files (NON RECOVERABLE!!! D:)")
    parser_concat.set_defaults(func=concat)

    if len(sys.argv) <= 1:
        sys.argv.append('--help')

    options = parser.parse_args()

    options.func(options)
