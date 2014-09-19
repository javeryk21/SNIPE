#!/usr/bin/python

print "Mbox parser"

"""This is an mbox filter. It scans through an entire mbox style mailbox
and writes the messages to a new file. Each message is passed
through a filter function which may modify the document or ignore it.

The passthrough_filter() example below simply prints the 'from' email
address and returns the document unchanged. After running this script
the input mailbox and output mailbox should be identical.
"""
import scipy.io
import mailbox, rfc822
import sys, os, string, re, numpy

LF = '\x0a'
subj_feat = ["immediately","alert","account","ebay","paypal","your","bank","amazon","inquiry","order","card","important","purdue","notice"]
doc_feat = ["inquiry","order","card","dear","email","e-mail","university","purdue","prudue","freeze","suspend","hold","ebaystatic","amazon","login","user","receive","immediately","alert","account","ebay","paypal","your","bank","credit","privacy","support","verify","return","confirm","now","please","target","our","service","security","status","signin","reply","below","password","username","access","microsoft","online","link","member","respond","notification","click","only","thank","item","policy","protect","customer","ensure","america","system","fraud","notice","forged","courier","verification","provide","complete","justify","client","restore","recently","inconvenience","inconveneince","billing","bill","assistance","identity","request","apologize","need","check","process","update","updated","protection","unusual","error","problem","mistake","issue","transaction","important","customers","money","cash","attempt","offer","change","confirmation","confirm","authorize","unauthorize","balance"]

doc_flg = [0] * 102
subj_flg = [0] * 14
msg_mtrx = []
test_mtrx = []
cont_type = None
cont_dict = {}
type_cont = 0 
subject = None
charset = None
encoding = None
attach = None
img_link = re.compile("\<a href=\s*\"(.*?)\"\>\<img src=\s*\"(.*?)\".*?\/a\>",re.M|re.S|re.I)
link_regex = re.compile('\s*https?://.*\s*$')

def main ():
	total_email_types = 0
	if len(sys.argv) != 3:
		print "Correct use: ./email_to_vector.py input_file.mbox output_file.out"
		sys.exit(0)
	
	#print "Lengths: ",len(subj_feat), len(doc_feat)
	#for i in range(0, len(doc_feat)):
	#	print (i+1), "Word:", doc_feat[i]
	
	mailboxname_in = sys.argv[1]
	mailboxname_out = sys.argv[2]
	process_mailbox (mailboxname_in, mailboxname_out, passthrough_filter)
	#print msg_mtrx[0]

	matrix = numpy.asarray(msg_mtrx, dtype='double')
	scipy.io.savemat(mailboxname_out + '.mat', mdict={'matrix':matrix})
	
# 	matrix = numpy.asarray(test_mtrx, dtype='double')
# 	scipy.io.savemat('testing26k.mat', mdict={'matrix':matrix})
	
	for key, value in cont_dict.items():
		#print key,value
	   	total_email_types += value

	for key,value in cont_dict.items():
		print key, (value / float(total_email_types)) * 100

def passthrough_filter (msg, document):
	"""This prints the 'from' address of the message and
	returns the document unchanged.
	"""

	#header info
	global subject
	subject = msg.get('Subject')
# 	print "Subject: ", subject

# 	print "Content type: ", msg.get("Content-Type")
# 
# 	global charset
# 	charset = msg.get('charset')
# 	print "Charset: ", charset
# 
# 	global encoding
# 	encoding = msg.get('Content-Transfer-Encoding')
# 	print "Encoding: ", encoding
# 
# 	global attach
# 	attach = msg.get('Content-Disposition')
# 	print "Attachment: ", attach

# 	global subject
# 	subject = msg.get('Subject')

	global flg_cont
	flg_cont = 0
	if cont_type != None:
	   	if cont_dict.has_key(cont_type.lower()):
			cont_dict[cont_type.lower()] += 1
	   	else:
		 	cont_dict[cont_type.lower()] = 1
	   	if "html" in cont_type.lower():
		 	global type_cont
		 	type_cont = 1

	return document

def process_mailbox (mailboxname_in, mailboxname_out, filter_function):
	'''This processes a each message in the 'in' mailbox and optionally
	writes the message to the 'out' mailbox. Each message is passed to
	the	 filter_function. The filter function may return None to ignore
	the message or may return the document to be saved in the 'out' mailbox.
	See passthrough_filter().
	'''

	# Open the mailbox.
	mb = mailbox.UnixMailbox (file(mailboxname_in,'r'))
	#fout = file(mailboxname_out, 'w')
	spam_flg = 0
	msg_stats = []

	msg = mb.next()
	flg_msg = 0
	while msg is not None:
		if spam_flg == 1:
			#msg = mb.next()
			spam_flg = 0
		# Properties of msg cannot be modified, so we pull out the
		# document to handle is separately. We keep msg around to
		# keep track of headers and stuff.
		document = msg.fp.read()
		document = filter_function (msg, document)
		if document is not None:
			link_img_flg = 0
			flg_http = 0
			flg_num_links = 0
			img_flg = 0
			attach_flg = 0
			encode_flg = 0
			charset_flg = 0
			
			for i in range(0, len(subj_flg)):
				subj_flg[i] = 0
			for i in range(0, len(doc_flg)):
				doc_flg[i] = 0

			if link_regex.match(document):
				msg = mb.next()
				continue
			else:
				flg_msg += 1
		
			#print("before for loop\n")
# 			for x in range (0, flg_char):
# 				if document[x].isdigit():
# 			   		flg_dig+=1
# 				elif document[x] in 'aeiouAEIOU':
# 			   		flg_vowel+=1
# 				elif not document[x] in 'aeiouAEIOU':
# 			   		flg_cons+=1
# 				else:
# 			   		flg_symbol+=1
			if "Content-Disposition: attachment".lower() in document.lower():
					#print "we have an attachment"
					attach_flg = 1
				
			if "Content-Transfer-Encoding: base64".lower() in document.lower():
					#print "we have an encoding"
					encode_flg = 1
				
			if 'charset="utf-8"' in document.lower() or 'charset="us-ascii"' in document.lower():
					#print "we have a charset"
					charset_flg = 1

			if subject != None:
				for i in range(0, len(subj_feat)):
					if subj_feat[i] in subject.lower():
						subj_flg[i] = 1
			
			for i in range(0, len(doc_feat)):
				if doc_feat[i] in document.lower():
					doc_flg[i] = 1
					
			flg_http = document.count('http')
			flg_num_links = document.count('href')
			if img_link.match(document) is not None:
				#print "we have a match!"
				link_img_flg = 1
			if "<img" or "< img" in document.lower():
				img_flg = 1;   				
			
			for i in range(0, len(subj_flg)):
				msg_stats.append(subj_flg[i])
				
			for i in range(0, len(doc_flg)):
				msg_stats.append(doc_flg[i])
							
			msg_stats.append(flg_num_links)
			msg_stats.append(flg_http)
			msg_stats.append(link_img_flg)
			msg_stats.append(img_flg)
			msg_stats.append(attach_flg)
			msg_stats.append(encode_flg)
			msg_stats.append(charset_flg)
			
			if flg_msg <= 40000:
				msg_mtrx.append(msg_stats)
			else:
				test_mtrx.append(msg_stats)
				
			msg_stats = []
			#if flg_msg % 1 == 0:
			   #print ("still here %d\n"% flg_msg) 
			msg = mb.next()

	print ("total phish msgs: %d\n" % flg_msg)
	#fout.close()


def write_message (fout, msg, document):
	"""This writes an 'rfc822' message to a given file in mbox format.
	This assumes that the arguments 'msg' and 'document' were generate
	by the 'mailbox' module. The important thing to remember is that the
	document MUST end with two linefeeds ('\n'). It comes this way from
	the mailbox module, so you don't need to do anything if you want to
	write it unchanged. If you modified the document then be sure that
	it still ends with '\n\n'.
	"""
	#msg is the header information
	fout.write (msg.unixfrom)
	for l in msg.headers:
		fout.write (l)
	fout.write (LF)
	fout.write (document) # this is just the email message

if __name__ == '__main__':
	main ()
