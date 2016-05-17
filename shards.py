import csv, sys, json

def process_shards_table():
	filename = 'TAB_filters.txt'
	csv.register_dialect('shards', delimiter='\t', quoting=csv.QUOTE_NONE)
	rows = []
	with open(filename, newline='') as f:
		next(f)
		next(f)
		next(f)
		#dialect = csv.Sniffer().sniff(f.read(1024), delimiters='\t ')
		reader = csv.reader(f, 'shards')
		try:
			for row in reader:
				if len(row) == 21:
					rows.append(row)
					#print(row)
		except csv.Error as e:
			sys.exit('file {}, line {}: {}'.format(filename, reader.line_num, e))

	shard_filters = []
	shard_dict_keys=list(map(str.strip,rows[0]))
	for row in rows[1:]:
		d = dict(zip(shard_dict_keys,map(str.strip, row)))
		shard_filters.append(d)
		#print(shard_dict_keys[-1])
	return shard_filters

shards_filters = process_shards_table()
# Writing JSON data
with open('shards.json', 'w') as f:
     json.dump(shards_filters, f)
