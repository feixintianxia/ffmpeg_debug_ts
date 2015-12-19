# WHAT IS THIS #

A visualization tool used to analyse timestamp gap in videos. Especially for videos that have data lost during streaming.

# INSTALLTION #

1. `FFMPEG` is used for getting timestamp datas frome videos. You can get pre-built binaries from zeranoe 
	- `zeranoe`: [http://ffmpeg.zeranoe.com/builds/](http://ffmpeg.zeranoe.com/builds/)

2. `python` + `numpy` + `matplotlib` is used for visualization. For simply, just install `python-xy` or `winpython`.
	- `python-xy`: [http://sourceforge.net/projects/python-xy/](http://sourceforge.net/projects/python-xy/)
	- `winpython`: [https://winpython.github.io/](https://winpython.github.io/)

# HOW TO USE #

`$ python ffmpe_debug_ts.py -h`

	Usage: ffmpeg\_debug\_ts.py [options]
	
	Options:
	  -h, --help            show this help message and exit
	  -i INPUT, --input=INPUT
	                        movie to be analyzed
	  -l LOG, --log=LOG     log to be analyzed if you don't specify movie
	  -o OUT, --out=OUT     Name for saved picture.
	  -s START, --start=START
	                        start time
	  -e END, --end=END     end time
	  -d DECODER, --decoder=DECODER
	                        Decoder type: ffmpeg or ffprobe. [ffmpeg]
	  -t THRESHOLD, --threshold=THRESHOLD
	                        Time inc above the threshold will trigger error
	                        report.
	  -c, --compress        Whether use log scaling axises. [0]
	  -k SELECT, --select=SELECT
                        select time-stamp type for showing. [pkt_pts,pkt_dts]

# EXAMPLES #

> $ python ffmpeg_debug_ts.py -i $MEDIA_PATH/movie1.flv

![movie1-all](README.data/movie1.flv.ffmpeg.log.png)

- The left column is timestamp delta for each packet with its previous packet. In normal case without data lost, it should be a horizontal line.
- The right colume is the total packets number at current time. In nomal case it should be a incline slash.
- There seems to be a lot of frame lost in the video stream. While the audio lost seems not serious.

To view the data lost detail. We can use the `-c` and `-e` options to zoom in data lost areas. Since we have decoded `movie1.flv` in the previous command, there is no need to repeat. To save time, we reuse the previous log by simply using `-l` option.

> $ python ffmpeg_debug_ts.py -l $MEDIA_PATH/movie1.flv.ffmpeg.log -s 7000 -e 8000

![movie1-cut](README.data/movie1.flv.ffmpeg.log.7000~8000.png)

Sometimes when data out of compliance, timestamps can go messy. Following is a movie2 actually has only 5-second long. But somehow it has some incorrect data at the tail, make the timestamp jump from 00:00:05 to 00:30:00.

> $ python ffmpeg_debug_ts.py -i $MEDIA_PATH/movie2.flv

![movie2](README.data/movie2.flv.ffmpeg.log.png)

To in case timestamp sudden change compress the compliant data area in axises, we can use `-c` option to log-scale the axises.

> $ python ffmpeg_debug_ts.py -l $MEDIA_PATH/movie2.flv.ffmpeg.log -c

![movie2-logaxis](README.data/movie2.flv.ffmpeg.log.logaxis.png)