import requests
from requests.adapters import HTTPAdapter
from urllib3 import Retry
from tweetHistory import TweetHistory

# Setup retry strategy
session = requests.Session()
retries = Retry(total=5,
                backoff_factor=0.1,
                status_forcelist=[500, 502, 503, 504])
session.mount('https://', HTTPAdapter(max_retries=retries))

twitter_list = ['artblocks_io', 'memeland', 'pudgypenguins', 'CryptoDickbutts', 'goblintown',
                'ChimpersNFT', 'wolfdotgame', 'huxleysaga', 'DigiDaigaku',
                'LuckyNFTNews', 'GutterCatGang', 'OthersideMeta', 'yugalabs', 'BoredApeYC',
                "tylerxhobbs", "ArtOnBlockchain", "zancan", "RTFKT", "apecoin", "CryptoGarga",
                "GordonGoner", "veefriends", "proof_xyz", "AzukiOfficial",
                "cryptopunksnfts", "coolcats", "doodles", "6529collections", "frankdegods",
                "DeezeFi"
                ]

summary_list = []
for user in twitter_list:
    print("Getting tweets for: " + user)
    tweet_list = TweetHistory(user, session)
    summary_list.append(tweet_list.get_summary())

summary_list = sorted(summary_list, key=lambda x: float(x['average_impressions']), reverse=True)
print("Summary:")
for summary in summary_list:
    print(summary['user'] + ": " + str(summary['average_impressions']))
