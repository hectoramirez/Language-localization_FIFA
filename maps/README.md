# Results

This folder contains [Plotly](https://plotly.com/python/)'s maps which summarize the results obtained in `FIFA_localization.ipynb`. [Click on the following links!]

* [`countries_covered.html`](https://hectoramirez.github.io/FIFA/countries_covered.html): Shows the countries where one or more of the languages already included in the FIFA game are spoken. We notice that the __Balkanic countries__ and the __Southeast Asia__ are not covered by the current available languages.

* [`countries_IR.html`](https://hectoramirez.github.io/FIFA/countries_IR.html): Here we localize languages not included in the game and highlight them by the international reputation (IR) of players that speak that language. This illustrates that languages like __Catalan__, __Slovenian__, __Croatian__, __Bosnian__ or __Hungarian__ are spoken by well-known players and this could influence the playability of the game in those countries/regions.

* [`tweets_coordinates.html`](https://hectoramirez.github.io/FIFA/tweets_coordinates.html): Only a small portion of the world's tweets (almost 1%) contain exact geolocation. In our dataset, they sum up to almost 500 tweets. This tweets are located here in a map colored by their sentiment. We showed that this subset is not enough to gather conclusions.

* [`countries_sentiment.html`](https://hectoramirez.github.io/FIFA/countries_sentiment.html): We processed the tweets by the manually-set user location, found a belonging country and associated a main language for that country. We then localize those languages in a map and colored them by mean sentiment. We found that __Bulgarian__, __Hebrew__, __Hindi__ and __Irish__ are the countries' languages -not included in the game- where people speak more positively.

* [`countries_IR_sentiment.html`](https://hectoramirez.github.io/FIFA/countries_IR_sentiment.html): Previously, we found out that localizing by IR some languages stand out whereas by sentiment, others. Here we aimed to select one or more language which stands out by both attributes. Interestingly, __Hebrew__ which ranks second by a well-above-average sentiment score ranks 10th by IR and thus is the most prominent language to target.