import re


# Returns True if the string passed is a valid URL, returns false if not.
def isurl(string):
    urlregex = r'https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)'  # courtesy of stackoverflow
    if re.search(urlregex, string) is not None:
        return True
    else:
        return False


# Converts an URL to short url if it is not already.
# TODO: Find a better solution.
#       This is a very bad solution, some edge cases of URLs valid for yt-dlp might not be valid here
#       but I don't want to introduce a further dependency on an external library for now.
#       A search by full URL in the database is also not a good solution.
def converttoshurl(string):
    shurlregex = r'(?<=\?v=).*'  # courtesy of stackoverflow
    if isurl(string) is True:
        shurl = re.search(shurlregex, string)
        return shurl.group()
    else:
        return string
