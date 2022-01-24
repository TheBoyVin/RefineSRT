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
        next_less = False
        faulty_sub = []

        self.short = short
        self.long = long
        self.not_adjusted = not_adjusted
        self.next_less = next_less
        self.faulty_sub = faulty_sub

    def check_next(self):
        t1 = str(self.current_end)
        t2 = str(self.next_start)
        end_int = int(t1[6 : ].replace(',', ''))
        next_start_int = int(t2[6 : ].replace(',', ''))

        end_min, next_start_min = int(t1[3 : 5]), int(t2[3 : 5])
        end_sec, next_start_sec = int(t1[6 : 8]), int(t2[6 : 8])

        text1 = str(self.next_duration)
        text2 = text1[6:].replace(',', '')
        next_num = int(text2)
        self.next_less = False

        if(next_start_int-end_int) < 0 and (next_start_min-end_min) == 0:
            self.next_less = True
            self.next_start += {'milliseconds': (-(next_start_int-end_int) + self.margin)}
            self.current_end  = self.next_start
    
            if next_num > 5000:
                #Do not edit end time here
                self.next_end = self.next_end
            elif next_num < 1000:
                self.next_end = self.next_start + {'milliseconds': (3000 + self.margin)}
            else:
                self.next_end = self.next_start + {'milliseconds': (next_num + self.margin)}

        elif self.current_end > self.next_start:
            print(f'Adjust {self.index+1} manually')
            if end_min > next_start_min:
                self.next_start += {'seconds': ((60 - next_start_sec) + (end_sec + 2))}
            
            elif end_min == next_start_min:
                 self.next_start += {'seconds': ((60 - next_start_sec) + (end_sec + 2))}
        
        else:
            if self.current_end < self.current_start:
                print(f'Adjusting {self.index} manually')
                dur = str(self.current_start - self.current_end)
                sec = int(dur[6 : 8])
                self.current_end += {'seconds': (sec + 2)}

    #fn to refine duration
    def refine_duration(self):
        for sub in self.subs:
            index = sub.index
            margin = randint(0, 50)
            duration = sub.duration
            self.duration = duration
            self.margin = margin

            self.index = index
            text1 = str(duration)
            text2 = text1[6:]
            text3 = text2.replace(',', '')
            num = int(text3)

            try:
                self.next_sub = self.subs[index]
            except:
                print('This is the last subtitle')

            current_start = sub.start
            current_end = sub.end
            next_start = self.next_sub.start
            next_end = self.next_sub.end
            next_duration = self.next_sub.duration

            self.current_start = current_start
            self.current_end = current_end
            self.next_start = next_start
            self.next_end = next_end
            self.next_duration = next_duration

            self.check_next()
            if self.next_less == True:
                self.next_sub.start, self.next_sub.end = self.next_start, self.next_end

            if num < 1000:
                remainder = 1000 - num
                ''' check start time of next subtitle first, subs[index] gets the next subtitle '''
                try:
                    next_sub = self.subs[index]
                except:
                    print('No next subtitle, this is the last subtitle')
                    
                else:
                    ''' convert tail difference between subtitles to a number'''
                    current_end = sub.end
                    next_start = next_sub.start
                    next_end = next_sub.end

                    self.current_end = current_end
                    self.next_start = next_start
                    self.next_end = next_end

                    self.check_next()
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
                                ptext2 = ptext1[6:]
                                ptext3 = ptext2.replace(',', '')
                                previous_duration = int(ptext3)

                                if previous_duration > (1000 + (remainder + margin)):
                                    ''' shift end time of previous subtitle '''
                                    previous_sub.end += {'milliseconds': -(remainder + margin)}
                                    sub.start += {'milliseconds': -(remainder + margin)}

                                else:
                                    nxt_duration = next_sub.duration
                                    ntext1 = str(nxt_duration)
                                    ntext2 = ntext1[6:]
                                    ntext3 = ntext2.replace(',', '')
                                    next_duration = int(ntext3)

                                    if next_duration > (1000 + (remainder + margin)):
                                        ''' shift start time of next subtitle '''
                                        next_sub.start += {'milliseconds': (remainder + margin)}
                                        sub.end += {'milliseconds': (remainder + margin)}

                                    elif next_duration < (1000 + (remainder + margin)):
                                        #case where subs are smash synced
                                        ''' shift start time of next subtitle '''
                                        self.next_sub.start += {'milliseconds': (remainder + margin)}
                                        sub.end += {'milliseconds': (remainder + margin)}
                                        #adjust next sub duration to roughly 2 seconds
                                        self.next_sub.end += {'milliseconds': (remainder + randint(1000, 3000))}

                    else:
                        sub.end += {'milliseconds': remainder + margin}

                self.short += 1

            if num > 5000:
                excess = num - 5000

                #for smash synced cases
                if num > 10000:
                    sub.start += {'milliseconds': (excess + margin)}
                    self.faulty_sub.append(self.index)

                #for normal cases
                else:
                    sub.end += {'milliseconds': -(excess + margin)}
                    

                self.long += 1
            
            self.current_start = sub.start
            self.current_end = sub.end

        if self.faulty_sub:
            faults = str(self.faulty_sub)[1: -1]
            self.faults = faults
            print(f'Check sub(s) {faults} manually and refine again.')

        print(f'Refined {self.short} subtitles of less than 1 second and {self.long} subtitles of longer than 5 seconds, while {self.not_adjusted} failed.')
    def run(self):
        self.refine_duration()
        self.subs.save('./uploads/refined.srt', encoding='utf-8')
        file = "./uploads/refined.srt"
        location = "./uploads/refined.srt"
        path = os.replace(file, location)

if __name__ == '__main__':
    Refine().run()