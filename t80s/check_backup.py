import hashlib
import os
import re
import sqlite3
import tarfile

# Mark True/False to check each part of backup.
check_bkpdir = False
check_tarfile = True
calculate_diff = False
drop_tarfile_table = True

# local test
# backup_directory = "/Users/william/Downloads/bacula-7.4.1/"
# files_prefix = '^/Users/william/Downloads/'  # Will remove this prefix from filenames.
# tar_file = "/Users/william/Downloads/bacula-7.4.1.tar.gz"

# STO01 - T80S
backup_directory = "/mnt/data/cam01/data/images/"
files_prefix = '^/mnt/data/cam01/data/images/'  # Will remove this prefix from filenames.
tar_file = "/dev/nsa0"

hash_type = 'md5'
db_file = "backup_data.db"

conn = sqlite3.connect(db_file)
c = conn.cursor()

if drop_tarfile_table:
    try:
        c.execute("DROP TABLE md5_backup")
        conn.commit()
    except sqlite3.OperationalError:  # If db does not exists
        pass

try:
    c.execute("CREATE TABLE md5_backup (filename text, md5 text)")
    c.execute("CREATE TABLE md5_files (filename text, md5 text)")
    conn.commit()
except sqlite3.OperationalError:  # If db already exists
    pass

chunk_size = 100 * 1024

# tar_checkfile = datetime.datetime.utcnow().strftime("%Y%m%d.txt")
# tarcheck_fp = open(tar_checkfile, "w")

# Backup directory
if check_bkpdir:
    for root, dir, files in os.walk(backup_directory):
        for file in files:
            sql_filename = re.sub(files_prefix, "", "%s/%s" % (root, file))
            a = c.execute("select * from md5_files where filename=?", (sql_filename,))
            if len(a.fetchall()) < 1:
                h = hashlib.new(hash_type)
                with open("%s/%s" % (root, file), "r") as fp:
                    data = fp.read(chunk_size)
                    while data:
                        h.update(data)
                        data = fp.read(chunk_size)
                md5 = h.hexdigest()
                c.execute("insert into md5_files values (?, ?)", (sql_filename, md5))
                conn.commit()
                # tarcheck_fp.write("%s    %s\n" % (md5, sql_filename))
                print("%s    %s" % (md5, sql_filename))
            else:
                print "Skipping file %s/%s" % (root, file)

# TAR file
if check_tarfile:
    tar = tarfile.open(tar_file, mode="r|")

    chunk_size = 100 * 1024
    store_digests = {}

    for member in tar:
        if member.isfile():
            a = c.execute("select * from md5_backup where filename=?", (member.name,))
            if len(a.fetchall()) < 1:
                f = tar.extractfile(member)
                h = hashlib.new(hash_type)
                data = f.read(chunk_size)
                while data:
                    h.update(data)
                    data = f.read(chunk_size)
                md5 = h.hexdigest()
                c.execute("insert into md5_backup values (?, ?)", (member.name, md5))
                print("%s    %s" % (md5, member.name))
                conn.commit()
            else:
                print "Skipping tar file %s" % member.name

# Calculate difference between two tables of backup to validate it.
if calculate_diff:
    c.execute("select * from md5_files a left join md5_backup b on (a.filename = b.filename)")
    missing = list()
    bad_md5 = list()
    for out in c:
        # output of query is: local_filename, local_md5, tape_filename, tape_md5
        ## Check both MD5
        if out[3] is None:
            missing.append(out[0])
        elif out[3] != out[1]:
            bad_md5.append(out)
    print "#" * 50 + " BACKUP REPORT " + "#" * 50
    print "#" * 50 + " missing files " + "#" * 50
    print "\n".join(missing)
    print "#" * 50 + "    bad md5    " + "#" * 50
    print "\n".join(["\t".join(i) for i in bad_md5])

conn.close()
