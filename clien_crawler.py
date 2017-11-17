import urllib2
import codecs
import time
import re
import sys

listUrl = "https://www.clien.net/service/board/%s?&po=%d"
articleUrl = "https://www.clien.net/service/board/%s/%s"
categories = ["cm_iphonien", "cm_vcoin", "cm_car", "cm_bike", "cm_mac", "cm_ku", "cm_andro", "cm_lego", "cm_gym", "cm_werule", "cm_nas", "cm_havehome", "cm_baby", "cm_coffee", "cm_cat", "cm_soccer", ]

INTERVAL = 1.5

def download(filename, url, waitOnError = True):
	while True:
		try:
			downloadFile = urllib2.urlopen(url)
		except:
			if waitOnError:
				print "Error occured! Wait 5 mins"
				time.sleep(60 * 5)
				continue
			else:
				break
		break

	print "Download file from: " + url
	
	output = open(filename,"wb")
	output.write(downloadFile.read())
	output.close()

def removeTags(line):
	newLine = re.sub("<[^>]+>", " ", line).strip()
	newLine = re.sub("&nbsp;", " ", newLine)
	newLine = re.sub("\s\s+", " ", newLine)
	#print newLine
		
	return newLine

def extractArticleIds(filename, prev = None):
	PREFIX = "/service/board/cm_[a-z]+/[0-9]+"

	articleIds = []

	f = codecs.open(filename, "r", "utf-8")

	for line in f:
		candiates = re.findall(PREFIX, line)

		if len(candiates) == 1:			
			articleId = re.findall("[0-9]+", candiates[0])
			articleId = articleId[0] if len(articleId) == 1 else None

			if articleId != None and (articleId not in articleIds) and (((prev is not None) and (articleId not in prev)) or prev is None):
				articleIds.append(articleId)

	f.close()

	print len(articleIds), articleIds
	return articleIds

def extractContent(filename):
	CATEGORY_PREFIX = "<span class=\"subject-category\">"
	CATEGORY_POSTFIX = "</span>"
	TITLE_PREFIX = "<title>"
	TITLE_POSTFIX = "</title>"
	POST_TIME_PREFIX = "<div class=\"post-time\">"
	BODY_PREFIX = "<meta name=\"description\" content=\""
	BODY_POSTFIX = "/>"

	category = ""
	title = ""
	postTime = ""
	body = ""

	f = codecs.open(filename, "r", "utf-8")

	for line in f:
		try:
			if CATEGORY_PREFIX in line.strip():
				category = removeTags(line.strip())
			
			if TITLE_PREFIX in line.strip():
				title = removeTags(line.strip())
			
			if POST_TIME_PREFIX in line.strip():
				postTime = removeTags(line.strip())

			if BODY_PREFIX in line.strip():
				body = line.strip()[len(BODY_PREFIX):-len(BODY_POSTFIX)]
		except:
			print "extractContent has errors."

	f.close()

	#print category.strip(), title.strip(), postTime.strip(), body.strip()
	return category.strip(), title.strip(), postTime.strip(), body.strip()

if __name__ == "__main__":
	downloadFilename = "./tmp.html"
	outputFilename = sys.argv[1] if len(sys.argv) > 1 else "./output.utf8"

	startIndex = int(sys.argv[2]) if len(sys.argv) > 2 else 0

	if len(sys.argv) > 3:
		categories = sys.argv[3:]

	for category in categories:
		previousIds = []

		for index in xrange(startIndex, sys.maxint):
			download(downloadFilename, listUrl % (category, index))

			ids = extractArticleIds(downloadFilename, previousIds)
			time.sleep(INTERVAL)

			for articleId in ids:
				download(downloadFilename, articleUrl % (category, articleId))

				subCategory, title, postTime, body = extractContent(downloadFilename)

				if subCategory != "" and title != "" and postTime != "" and body != "":
					f = codecs.open(outputFilename, "a", "utf-8")

					f.write("%s\t%s\t%s\t%s\t%s\n" % (category, postTime, subCategory, title, body))

					f.close()

				time.sleep(INTERVAL)

			if len(ids) == 0:
				break

			previousIds += ids
