import time, re, json, urllib2, praw, sys, urllib2, simplejson, Image, pyimgur, traceback

USERNAME = "user1234"           #Reddit username
PASSWORD = "pass1234"           #Reddit password
SUBREDDITS = "all"              #Subreddits to scan. Use '+' operand for multiple subreddits. i.e. ukpolitics+bikes
VERBOSE = True                  #print out stuff, or don't
IMGUR_ID = "123456789010abc"    #Imgur API key
IMAGE_PATH = "images"           #Path to images
CHILLAX_PERIOD = 601            #Time to wait in seconds after finding an Alot (seconds)
COMMENT_READ_SPEED =  10        #Time between scanning comments (seconds)

r = praw.Reddit(user_agent = 'alot9000 /1.0 by majorkong'
                'Url: http://majorkong.net')
r.login(USERNAME,PASSWORD)
already_done_ = []
alot_words = ['alot'] 

subreddit = r.get_subreddit(SUBREDDITS) 

def main():
    while True:   
        subreddit_comments = subreddit.get_comments()
        
        #It's important not to Alotify the same comment twice so 
        #we will append a comments ID code into this list. 
        already_done = []
        
        for comment in subreddit_comments:

            if 'alot' in comment.body and comment.id not in already_done:
                try: 
                    
                    everyone,loves,alots = comment.body.partition('alot ')
                    morealots = alots.split(' ',2)
                    alotofquery = morealots[1]

                    #Lets not bother with anything except 'Alot of' sentence construction for the time being.
                    if morealots[0] != 'of':
                        break
                    
                    alotofurl = ('https://ajax.googleapis.com/ajax/services/search/images?' +
                      'v=1.0&q='+alotofquery)
                      
                    alotofrequest = urllib2.Request(alotofurl, None, {'Referer': 'majorkong.net'})
                    alotofresponse = urllib2.urlopen(alotofrequest)
                    alotofresults = simplejson.load(alotofresponse)
                    
                    imageurl = alotofresults['responseData']['results'][0]['url']
                    
                    try:    
                        req = urllib2.Request(imageurl)
                        response = urllib2.urlopen(req)
                    except urllib2.HTTPError:
                        if VERBOSE:
                            print("hmm... so I couldn't load that image. Lets try another one.")
                        imageurl = alotofresults['responseData']['results'][1]['url']
                        req = urllib2.Request(imageurl)
                        response = urllib2.urlopen(req)
                         
                    
                    output = open(IMAGE_PATH + '/temp.png','wb')
                    output.write(response.read())
                    output.close()

                    background = Image.open(IMAGE_PATH + '/temp.png')
                    foreground = Image.open(IMAGE_PATH + '/alot_overlay.png')
                    imageresize = background.resize((400,300), Image.ANTIALIAS)
                    imageresize.save(IMAGE_PATH + '/resize.png', 'PNG', quality=75)
                    imageresize.paste(foreground, (0, 0), foreground)
                    imageresize.save(IMAGE_PATH + '/result.png', 'PNG')  
                    im = pyimgur.Imgur(IMGUR_ID)
                    uploaded_image = im.upload_image(IMAGE_PATH + '/result.png', title="Alot of " + morealots[1])
                    
                    comment.reply("Hello! I'm alot9000.\n\n"                                  
                                  "You said: \n\n"
                                  ">alot " + morealots[0] + " " + morealots[1] +"\n\n" 
                                  "I have generated the Alot of " + morealots[1] + " based on your comment: " + uploaded_image.link + "\n\n"
                                  "Have a lovely day. Please excuse me if I'm wrong. "
                                  "To read more about Alots visit [Hyperbole and a Half](http://hyperboleandahalf.blogspot.co.uk/2010/04/alot-is-better-than-you-at-everything.html)"
                                  )
                    
                    already_done.append(comment.id)
                    if VERBOSE:
                        print("I created a "+ morealots[1] +" Alot! Going to sleep for 10 minutes now...")
                    time.sleep(CHILLAX_PERIOD)
                except Exception, alotofexception:
                        print 'alot of exception: %s' % alotofexception
                        traceback.print_stack()
                        print sys.exc_traceback.tb_lineno
        if VERBOSE:               
            print("Scanned new comments from " + SUBREDDITS + ". Lets wait " + str(COMMENT_READ_SPEED) + " second(s) before trying again...")
        time.sleep(COMMENT_READ_SPEED)
            
if __name__ == "__main__":
    main()
