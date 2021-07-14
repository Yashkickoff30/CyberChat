from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer


analyzer = SentimentIntensityAnalyzer()


def analyzeUserSentiment(user, chat):
    data = {}
    total_positive = 0
    total_negative = 0
    total_neutral = 0
    total_compound = 0
    for key in chat.keys():
        if key == user:
            for msg in chat[key]:
                print("msg is: ", msg)
                analyzed_value = analyzer.polarity_scores(msg)
                if (analyzed_value['compound'] >= 0.05):
                    total_positive += 1
                elif (analyzed_value['compound'] > -0.05 and analyzed_value['compound'] < 0.05):
                    total_neutral += 1
                elif (analyzed_value['compound'] <= -0.05):
                    total_negative += 1
                total_compound += analyzed_value['compound']
                print("analysis: ", analyzed_value)
            cc_val = round((total_compound * 100)/len(chat[key]))
            print(key + '\'s total compound % = ', cc_val)
            if cc_val >= 10:
                data['verdict'] = 'happy'
                print('The user is in a happy mood')
            elif cc_val <= -10:
                data['verdict'] = 'sad'
                print('The user is in a sad mood')
            else:
                data['verdict'] = 'neutral'
                print('The user is in a neutral mood')
            data['username'] = key
            data['tp'] = total_positive
            data['tneg'] = total_negative
            data['tneu'] = total_neutral
            data['tcomp'] = cc_val
    return data
