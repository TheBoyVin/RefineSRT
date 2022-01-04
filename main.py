import pysrt
import os
from random import randint

''' loop over subtitles and change duration if caption exceeds 5 seconds or is less than 1 second '''
class Refine:
    #initialize Refine class
    def __init__(self):
        subs = pysrt.open('./uploads/upload.srt')
        self.subs = subs
        short = 0
        long = 0
        not_adjusted = 0

        self.short = short
        self.long = long
        self.not_adjusted = not_adjusted

    #fn to refine duration
    def refine_duration(self):
        for sub in self.subs:
            index = sub.index
            margin = randint(0, 50)
            duration = sub.duration
            #print(duration)

            text1 = str(duration)
            text2 = text1[7:]
            text3 = text2.replace(',', '')
            num = int(text3)

            if num < 1000:
                remainder = 1000 - num

                ''' check start time of next subtitle first, subs[index] gets the next subtitle '''
                try:
                    next_sub = self.subs[index]
                except:
                    ''' Reduce no of short subtitles, increase number of un adjusted '''
                    self.short -= 1
                    self.not_adjusted += 1
                    print('No next subtitle, this is the last subtitle')
                    print(f'Please manually adjust time codes for subtitle {sub.index}')
                    #pass
                else:
                    ''' convert tail difference between subtitles to a number'''
                    current_end = sub.end
                    next_start = next_sub.start

                    tail_diff = next_start - current_end

                    tail_text1 = str(tail_diff)
                    tail_text2 = tail_text1.replace(':', '')
                    tail_text3 = tail_text2.replace(',', '')
                    tail_difference = int(tail_text3)

                    if tail_difference < (remainder + 50):
                        try:
                            previous_sub = self.subs[index-2]
                        except:
                            pass
                        else:
                            ''' convert head difference between subtitles to a number'''
                            current_start = sub.start
                            previous_end = previous_sub.end

                            head_diff = current_start - previous_end

                            head_text1 = str(head_diff)
                            head_text2 = head_text1.replace(':', '')
                            head_text3 = head_text2.replace(',', '')
                            head_difference = int(head_text3)

                            if head_difference > (remainder + 50):
                                ''' shift start time of current subtitle '''
                                sub.start += {'milliseconds': -(remainder + margin)}

                            else:
                                ''' check duration of previous subtitle '''
                                prev_duration = previous_sub.duration
                                ptext1 = str(prev_duration)
                                ptext2 = ptext1[7:]
                                ptext3 = ptext2.replace(',', '')
                                previous_duration = int(ptext3)

                                if previous_duration > (1000 + (remainder + margin)):
                                    ''' shift end time of previous subtitle '''
                                    previous_sub.end += {'milliseconds': -(remainder + margin)}
                                    sub.start += {'milliseconds': -(remainder + margin)}

                                else:
                                    nxt_duration = next_sub.duration
                                    ntext1 = str(nxt_duration)
                                    ntext2 = ntext1[7:]
                                    ntext3 = ntext2.replace(',', '')
                                    next_duration = int(ntext3)

                                    if next_duration > (1000 + (remainder + margin)):
                                        ''' shift start time of next subtitle '''
                                        next_sub.start += {'milliseconds': (remainder + margin)}
                                        sub.end += {'milliseconds': (remainder + margin)}

                                    else:
                                        ''' Reduce no of short subtitles, increase number of un adjusted '''
                                        self.short -= 1
                                        self.not_adjusted += 1
                                        print(f'Please manually adjust time codes for subtitle {sub.index}')

                    else:
                        sub.end += {'milliseconds': remainder + margin}

                self.short += 1

                    #new_duration = sub.duration
                    #index = sub.index

                    #print(index)
                    #print(duration)
                    #print(new_duration)

            if num > 5000:
                excess = num - 5000

                sub.end += {'milliseconds': -(excess + margin)}

                self.long += 1

                #new_duration = sub.duration
                #print(duration)
                #print(new_duration)
        print(f'Refined {self.short} subtitles of less than 1 second and {self.long} subtitles of longer than 5 seconds, while {self.not_adjusted} failed.')

    def run(self):
        self.refine_duration()
        self.subs.save('./uploads/refined.srt', encoding='utf-8')
        file = "./uploads/refined.srt"
        location = "./uploads/refined.srt"
        path = os.replace(file, location)

if __name__ == '__main__':
    Refine().run()