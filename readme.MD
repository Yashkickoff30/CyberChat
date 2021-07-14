# Cyber - Chat

A Chat Application that detects Toxic Comments and performs Sentiment Analysis.

## Implemented using:

- Python
- Flask
- WebSockets
- CNN with Word Embedding
- Vader Sentiment
- Firebase RealTime Database

### DataSet Used:

The dataset that was used for Toxic Comment Classification was taken from [Kaggle](https://www.kaggle.com/c/jigsaw-toxic-comment-classification-challenge).

### Working:

- Once a user has logged into his account, he will be directed to the ChatPage.
- Whenever a user types in his message, it is being passed onto a ML model(built using CNN with Word Embedding) that performs Toxic Comment Classification.
- The Toxicity Classification result along with the message will be broadcasted to all the user in the Chat Session using WebSockets.

#### Toxicity Classification:

Based on the user's message the App classifies them into 3 broad categories:

- **Non - toxic Comment** represented by a ✅
- **Toxic Comment** represented by a ❗
- **Suspicious Comment** (represented by a Yellow Exclamation mark).

All the Toxic and Suspicious Comments will be accompanied by a set of tags that were found associated with the message.

#### Sentiment Analysis:

- The Sentiment Analysis is done using the [Vader Sentiment analysis](https://github.com/cjhutto/vaderSentiment).
- Based on the **compund** value of each comment it will be marked as either **Positive, Negative or Neutral**.
- The current mental state and the total number of Positive, Negative and Neutral comments of a user is displayed in the **Result** section.

### Scoring:

- At the end of a Chat session, a detailed analysis is presented to the user.
- The Toxicity meter is based on the conversations of the entire Chat Session(which includes all the users).
- The Sentiment Analyzer analyzes the sentiments of each and every user based on their messages in a Chat Session.
- The final sentiment score of the user is sent to the Database.
- When the next time a user revists **CyberChat**, a special Emoji will be displayed alongside his name, which is based on the sentiment score from the Database.
