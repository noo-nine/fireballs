## Idea:
1) Collect data from game during actual gameplay (stored in 'fireballs-data.csv' )
2) perform feature engineering to generate useful features for the model using raw data ( in 'adaboost.ipynb' )
3) Train adaboost with ( 'decision tree' as base estimator )
4) 'fireballs-generation.py' generates data for game replay (in 'replay-frames.csv'), data to predict safe positions for the player( ghost ) ( in 'replay-features.csv' )
5) use adaboost to predict ghost player positions
6) generate the game in replay mode ( using 'replay-frames.csv' ) with predicted positions of ghost player

### 1st Try:
Accuracy of the model: 67.5%
Drawbacks: 1) train the model to show positions either to the left of right of the current position
           2) predicting one of 6 the positions doesnt help the actual player move to safe space before hitting the obstacle ( fireballs )
