#!/bin/env python
#
#     manage_runs.py: utility for managing fastq files from auto_process
#     Copyright (C) University of Manchester 2014 Peter Briggs
#
#########################################################################
#
# manage_fastqs.py
#
#########################################################################

"""
Utility for managing Fastq files from auto_processing.

Functionality includes:

- report individal file sizes
- copy to another location
- create checksums
- make zip archive

"""

#######################################################################
# Imports
#######################################################################

import sys
import os
import optparse
import shutil
import tempfile
import zipfile
import bcftbx.utils as bcf_utils
import bcftbx.Md5sum as md5sum
import auto_process_ngs.utils as utils
import auto_process_ngs.applications as applications

#######################################################################
# Functions
#######################################################################

def get_fastqs(project):
    """Return fastq files within an AnalysisProject

    Given an AnalysisProject, yields

    (sample_name,fastq,actual_fastq)

    tuples for each fastq file in all samples, where

    - 'fastq' = the original fastq name
    - 'actual_fastq' = the 'actual' fastq location (if
      'fastq' is a symbolic link)

    Arguments:
      project: AnalysisProject instance

    """
    for sample in project.samples:
        for fq in sample.fastq:
            # Resolve links
            if os.path.islink(fq):
                target = bcf_utils.Symlink(fq).resolve_target()
            else:
                target = fq
            yield (sample.name,fq,target)

def write_checksums(project,filen=None,relative=True):
    """Write MD5 checksums for fastq files with an AnalysisProject

    Arguments:
      project: AnalysisProject instance
      filen: if supplied then checksums will be written
        to this file; otherwise they will be written to
        stdout (default)
      relative: if True (default) then fastq file names
        will be the basename; otherwise they will be the
        full paths.

    """
    if filen:
        fp = open(md5file,'w')
    else:
        fp = sys.stdout
    for sample_name,fastq,fq in get_fastqs(project):
        if relative:
            name = os.path.basename(fq)
        else:
            name = fq
        fp.write("%s  %s\n" % (md5sum.md5sum(fq),name))
    if filen:
        fp.close()

def copy_to_dest(f,dirn):
    """Copy a file to a local or remote destination

    Raises an exception if the copy operation fails.

    Arguments:
      f: file to copy (must be local)
      dirn: target directory, either local or of the form
        "[user@]host:dir"
    
    """
    if not os.path.exists(f):
        raise Exception("File %s doesn't exist" % f)
    user,host,dest = utils.split_user_host_dir(dirn)
    remote = (host is not None)
    if not remote:
        # Local copy
        shutil.copy(f,dirn)
    else:
        # Remote copy
        try:
            scp = applications.general.scp(user,host,f,dest)
            print "Running %s" % scp
            scp.run_subprocess()
        except Exception, ex:
            raise Exception("Failed to copy %s to %s: %s" % (f,dirn,ex))

#######################################################################
# Main program
#######################################################################

if __name__ == "__main__":

    # Command line
    p = optparse.OptionParser(usage="\n\t%prog DIR\n\t%prog DIR PROJECT\n\t%prog DIR PROJECT copy [[user@]host:]DEST\n\t%prog DIR PROJECT md5\n\t%prog DIR PROJECT zip",
                              description="Fastq management utility. If only DIR is "
                              "supplied then list the projects; if PROJECT is supplied "
                              "then list the fastqs; 'copy' command copies fastqs for the "
                              "specified PROJECT to DEST on a local or remote server; 'md5' "
                              "command generates checksums for the fastqs; 'zip' command "
                              "creates a zip file with the fastq files.")
    options,args = p.parse_args()
    # Get analysis dir
    try:
        dirn = args[0]
        print "Loading data for analysis dir %s" % dirn
    except IndexError:
        p.error("Need to supply the path to an analysis dir")
        sys.exit(1)
    analysis_dir = utils.AnalysisDir(dirn)
    # Get specified project
    try:
        project_name = args[1]
    except IndexError:
        # List projects and exit
        print "Projects:"
        for project in analysis_dir.projects:
            print "%s" % project.name
        if analysis_dir.undetermined:
            print "_undetermined"
        sys.exit(0)
    sys.stdout.write("Checking for project '%s'..." % project_name)
    project = None
    for prj in analysis_dir.projects:
        if prj.name == project_name:
            project = prj
            break
    if project is None:
        if project_name == "_undetermined" and analysis_dir.undetermined:
            project = analysis_dir.undetermined
        else:
            print "not found"
            sys.stderr.write("FAILED cannot find project '%s'\n" % project_name)
            sys.exit(1)
    print "ok"
    # Check for a command
    try:
        cmd = args[2]
    except IndexError:
        # List fastqs and exit
        total_size = 0
        n_fastqs = 0
        for sample_name,fastq,fq in get_fastqs(project):
            # File size
            fsize = os.lstat(fq).st_size
            print "%s\t%s%s\t%s" % (sample_name,
                                    os.path.basename(fq),
                                    ('*' if os.path.islink(fastq) else ''),
                                    bcf_utils.format_file_size(fsize))
            total_size += fsize
            n_fastqs += 1
        # Summary
        print "Total:\t%s" % bcf_utils.format_file_size(total_size)
        print "%d %ssamples" % (len(project.samples),
                                ('paired-end ' if project.info.paired_end else ''))
        print "%d fastqs" % n_fastqs
        sys.exit(0)
    # Perform command
    if cmd not in ('copy','zip','md5'):
        p.error("Unrecognised command '%s'\n" % cmd)
        sys.exit(1)
    if cmd == 'copy':
        # Get the destination
        try:
            dest = args[3]
        except IndexError:
            p.error("Need to supply a destination for 'copy' command")
            sys.exit(1)
        # Make a temporary MD5 file
        tmp = tempfile.mkdtemp()
        try:
            md5file = os.path.join(tmp,"%s.chksums" % project.name)
            sys.stdout.write("Creating checksum file %s..." % md5file)
            write_checksums(project,filen=md5file)
            print "done"
            print("Copying to %s" % dest)
            copy_to_dest(md5file,dest)
        finally:
            shutil.rmtree(tmp)
        # Copy fastqs
        fastqs = get_fastqs(project)
        nfastqs = len(fastqs)
        i = 0
        for sample_name,fastq,fq in get_fastqs(project):
            i += 1
            print "(%2 d/%2 d) %s" % (i,nfastqs,fq)
            copy_to_dest(fq,dest)
    elif cmd == 'md5':
        # Generate MD5 checksums
        md5file = "%s.chksums" % project.name
        if os.path.exists(md5file):
            sys.stderr.write("ERROR checksum file '%s' already exists\n" % md5file)
            sys.exit(1)
        sys.stdout.write("Creating checksum file %s..." % md5file)
        write_checksums(project,filen=md5file)
        print "done"
    elif cmd == 'zip':
        # Create a zip file
        zip_file = "%s.zip" % project.name
        if os.path.exists(zip_file):
            sys.stderr.write("ERROR zip file '%s' already exists" % zip_file)
            sys.exit(1)
        print "Creating zip file %s" % zip_file
        zz = zipfile.ZipFile(zip_file,'w')
        # Add fastqs
        for sample_name,fastq,fq in get_fastqs(project):
            zz.write(fq,arcname=os.path.basename(fq))
        # Make a temporary MD5 file
        tmp = tempfile.mkdtemp()
        try:
            md5file = os.path.join(tmp,"%s.chksums" % project.name)
            sys.stdout.write("Creating checksum file %s..." % md5file)
            write_checksums(project,filen=md5file)
            print "done"
            print("Adding to %s" % zip_file)
            zz.write(md5file,arcname=os.path.basename(md5file))
        finally:
            shutil.rmtree(tmp)
        zz.close()
        
