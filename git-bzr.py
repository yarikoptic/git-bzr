#!/usr/bin/env python
import os
from os.path import join as pjoin, abspath, isdir, isfile, dirname
import sys
import subprocess

import argparse

'''
  def get_location(remote)
    l = `git config git-bzr.#{remote}.location`.strip
    if l == ""
      puts "Cannot find bazaar remote with name `#{remote}`."
      exit
    end
    l
  end
  
  def fetch(*args)
    remote = args.shift
    unless remote && args.empty?
      puts "Usage: git bzr fetch branchname"
      exit
    end
    location = get_location(remote)

    git_map = File.expand_path(File.join(git_dir, "bzr-git", "#{remote}-git-map"))
    bzr_map = File.expand_path(File.join(git_dir, "bzr-git", "#{remote}-bzr-map"))

    if !File.exists?(git_map) && !File.exists?(bzr_map)
      print "There doesn't seem to be an existing refmap. "
      puts "Doing an initial import"
      FileUtils.makedirs(File.dirname(git_map))
      `(bzr fast-export --export-marks=#{bzr_map} --git-branch=bzr/#{remote} #{location}) | (git fast-import --export-marks=#{git_map})`
    elsif File.exists?(git_map) && File.exists?(bzr_map)
      puts "Updating remote #{remote}"
      old_rev = `git rev-parse bzr/#{remote}`
      `(bzr fast-export --import-marks=#{bzr_map} --export-marks=#{bzr_map} --git-branch=bzr/#{remote} #{location}) | (git fast-import --quiet --export-marks=#{git_map} --import-marks=#{git_map})`
      new_rev = `git rev-parse bzr/#{remote}`
      puts "Changes since last update:"
      puts `git shortlog #{old_rev.strip}..#{new_rev.strip}`
    else
      puts "One of the mapfiles is missing! Something went wrong!"
    end
  end
  
  def push(*args)
    remote = args.shift
    unless remote && args.empty?
      puts "Usage: git bzr push branchname"
      exit
    end
    location = get_location(remote)
    
    if `git rev-list --left-right HEAD...bzr/#{remote} | sed -n '/^>/ p'`.strip != ""
      puts "HEAD is not a strict child of #{remote}, cannot push. Merge first"
      exit
    end
    
    if `git rev-list --left-right HEAD...bzr/#{remote} | sed -n '/^</ p'`.strip == ""
      puts "Nothing to push. Commit something first"
      exit
    end
    
    git_map = File.expand_path(File.join(git_dir, "bzr-git", "#{remote}-git-map"))
    bzr_map = File.expand_path(File.join(git_dir, "bzr-git", "#{remote}-bzr-map"))

    if !File.exists?(git_map) || !File.exists?(bzr_map)
      puts "We do not have refmapping yet. Then how can I push?"
      exit
    end
    
    `(git fast-export --import-marks=#{git_map} --export-marks=#{git_map} HEAD) | (cd #{location} && bzr fast-import --import-marks=#{bzr_map} --export-marks=#{bzr_map} -)`
  end    

  def git_dir
    `git rev-parse --git-dir`.strip
  end

  def run(cmd, *args)
    `git rev-parse 2> /dev/null`
    if $? != 0
      puts "Must be inside a git repository to work"
      exit
    end
    up = `git rev-parse --show-cdup`.strip
    up = "." if up == ""
    Dir.chdir(up) do
      __send__(cmd.to_s, *args)
    end
  end
end
'''

def shrun(cmd, ret_error=False, ret_code=False):
    proc = subprocess.Popen(cmd,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE,
                            shell=True)
    (out, err) = proc.communicate()
    if not (ret_error or ret_code):
        return out
    ret = [out]
    if ret_error:
        ret.append(err)
    if ret_code:
        ret.append(proc.returncode)
    return ret


def add(**args):
    if args['name'] in shrun('git remote show').split("\n"):
        raise OSError("There is already a remote with that name")
    if shrun('git config git-bzr.%(name)s.url' % args) != "":
        raise OSError("There is alread a bazaar branch with that name")
    if not isdir(pjoin(args['location'], ".bzr")):
        raise OSError("%(location)s is not a bazaar repository" % args)
    shrun('git config git-bzr.%(name)s.location %(location)s' % args)
    print "Bazaar branch %(name)s added. You can fetch it with " \
              "`git bzr fetch %(name)s`" % args


def fetch(**args):
    remote = args['branchname']
    location = get_location(remote)
    git_dir = abspath(get_git_dir())
    map_dir = pjoin(git_dir, 'bzr-git')
    git_map = pjoin(map_dir, '%s-git-map' % remote)
    bzr_map = pjoin(map_dir, '%s-bzr-map' % remote)
    if not isfile(git_map) and not isfile(bzr_map):
        print "There doesn't seem to be an existing refmap. "
        print "Doing an initial import"
        os.makedirs(map_dir)
        shrun('(bzr fast-export --export-marks=%(bzr_map)s '
              '--git-branch=bzr/%(remote)s %(location)s) | '
              '(git fast-import --export-marks=%(git_map)s)'
              % locals())
    if isfile(git_map) and isfile(bzr_map):
        print 'Updating remote', remote
        old_rev = rev_parse('bzr/%s' % remote)
        shrun('(bzr fast-export '
              '--import-marks=%(bzr_map)s '
              '--export-marks=%(bzr_map)s '
              '--git-branch=bzr/%(remote)s '
              '%(location)s) | '
              '(git fast-import '
              '--quiet '
              '--export-marks=%(git_map)s '
              '--import-marks=%(git_map)s)'
              % locals())
        new_rev = rev_parse('bzr/%s' % remote)
        print "Changes since last update:"
        print shrun('git shortlog %s..%s' % (old_rev, new_rev))
    else:
        raise OSError("One of the mapfiles is missing! "
                      "Something went wrong!")


def push(**args):
    remote = args['branchname']
    location = get_location(remote)
    lst = shrun('git rev-list --left-right HEAD...bzr/%s' % remote)
    
      puts "HEAD is not a strict child of #{remote}, cannot push. Merge first"
      exit
    end
    
    if `git rev-list --left-right HEAD...bzr/#{remote} | sed -n '/^</ p'`.strip == ""
      puts "Nothing to push. Commit something first"
      exit
    end



def get_location(remote):
    out = shrun('git config git-bzr.%s.location' % remote).strip()
    if out == "":
        raise OSError("Cannot find bazaar remote with name `%(s`."
                      % remote)
    return out


def get_git_dir():
    return rev_parse('--git-dir')


def rev_parse(arg):
    return shrun('git rev-parse %s' % arg).strip()
    

def main():
    # create the base parser with a subparsers argument
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()
    # add a sub-command "add"
    add_parse = subparsers.add_parser('add')
    add_parse.add_argument('name')
    add_parse.add_argument('location')
    add_parse.set_defaults(func=add)
    # add sub-commands  "fetch" "push"
    fetch_parse = subparsers.add_parser('fetch')
    fetch_parse.add_argument('branchname')
    fetch_parse.set_defaults(func=fetch)
    push_parse = subparsers.add_parser('push')
    push_parse.add_argument('branchname')
    push_parse.set_defaults(func=push)
    # parse arguments, run commands
    args = parser.parse_args()
    # check we're ok to go
    out, code = shrun('git rev-parse', ret_code=True)
    if code != 0:
        raise OSError("Must be inside a git repository to work")
    # change to root of git repository
    up = rev_parse('--show-cdup')
    if up != '':
        os.chdir(up)
    # run command
    args.func(**args.__dict__)


if __name__ == '__main__':
    main()
