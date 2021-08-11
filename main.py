from reddit_front import RedditFront
import diamanten
import sys, getopt

def main(argv):
    test = False
    try:
        opts, args = getopt.getopt(argv,"t")
    except getopt.GetoptError:
        print ('test.py [-t testrun]')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-t':
            test = True
    try:
        message = diamanten.create_message()
        print(message)

        if (not test):
            #RedditFront().postSuperstonkDaily(message)
            print("Not test")
        else:
            print("test")
    except Exception as e:
        print (str(e.__class__.__name__) + ": " + str(e))

if __name__ == "__main__":
    main(sys.argv[1:])
