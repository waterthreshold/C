BEGIN {
	count = 0
}
{
    if (NR > 1) {
		used_key="storage" count "_used="
		avail_key="storage" count "_avail="
		use_key = "storage" count "_use="
		mnt_key="storage" count "_mnt=" 
		size_key="storage" count "_size=" 
        s = s "&" size_key $2 "&" used_key $3 "&" avail_key $4 "&" use_key  $5 "&" mnt_key $6 
		count += 1
    }
}

END { print "storage_count=" count s }