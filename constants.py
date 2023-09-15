PLAYER_URL = "https://api.chess.com/pub/player/"
BULK_URL = "https://api.chess.com/pub/country/US/players"
REQUEST_HEADER = {'User-Agent': 'mark.sabotta@gmail.com'}
PLAYERS = 'players'
CHESS_BLITZ = 'chess_blitz'
LAST = 'last'
RATING = 'rating'
URL = 'url'
GAMES = 'games'
WHITE = 'white'
BLACK = 'black'
USERNAME = 'username'
RESULT = 'result'


#sample games query:
#{"games":[{"url":"https://www.chess.com/game/daily/550211543",
#"pgn":"[Event \"Let's Play!\"]\n[Site \"Chess.com\"]\n[Date \"2023.08.13\"]\n[Round \"-\"]\n[White \"jgarnette04\"]\n[Black \"MarcusSabotta\"]\n
#[Result \"0-1\"]\n[CurrentPosition \"r6Q/p1pn2pb/1pq3k1/5RP1/3P4/P6P/5P1K/8 w - - 1 30\"]\n[Timezone \"UTC\"]\n[ECO \"C00\"]\n
#[ECOUrl \"https://www.chess.com/openings/French-Defense-Knight-Variation-2...d5-3.exd5-exd5-4.d4\"]\n
#[UTCDate \"2023.08.13\"]\n[UTCTime \"20:55:58\"]\n[WhiteElo \"1151\"]\n[BlackElo \"1417\"]\n
#[TimeControl \"1/604800\"]\n[Termination \"MarcusSabotta won by resignation\"]\n[StartTime \"20:55:58\"]\n[EndDate \"2023.09.03\"]\n
#[EndTime \"17:06:16\"]\n[Link \"https://www.chess.com/game/daily/550211543\"]\n\n1. e4 {[%clk 140:04:07]} 1... e6 {[%clk 167:53:31]} 
#2. Nf3 {[%clk 127:46:21]} 2... d5 {[%clk 167:46:01]} 3. exd5 {[%clk 91:13:16]} 3... exd5 {[%clk 167:57:05]} 4. d4 {[%clk 77:35:29]} 
#4... Nf6 {[%clk 167:50:35]} 5. c4 {[%clk 167:38:57]} 5... Bg4 {[%clk 167:16:53]} 6. Nc3 {[%clk 167:49:17]} 
#6... Bb4 {[%clk 167:42:25]} 7. a3 {[%clk 167:58:41]} 7... Bxc3+ {[%clk 167:59:44]} 8. bxc3 {[%clk 166:08:09]} 8... O-O {[%clk 167:52:42]} 
#9. h3 {[%clk 144:04:20]} 9... Re8+ {[%clk 167:38:46]} 10. Be3 {[%clk 166:04:46]} 10... Bh5 {[%clk 167:23:46]} 11. Bd3 {[%clk 156:12:25]} 
#11... Ne4 {[%clk 166:46:57]} 12. O-O {[%clk 157:17:10]} 12... Nxc3 {[%clk 167:48:00]} 13. Qc2 {[%clk 146:35:52]} 13... dxc4 {[%clk 167:14:49]} 
#14. Bxh7+ {[%clk 155:24:32]} 14... Kh8 {[%clk 165:49:34]} 15. Qxc3 {[%clk 167:09:45]} 15... Kxh7 {[%clk 167:59:36]} 16. Ng5+ {[%clk 159:53:40]} 
#16... Kg8 {[%clk 152:28:30]} 17. Qxc4 {[%clk 157:33:57]} 17... Rxe3 {[%clk 167:57:15]} 18. Rfe1 {[%clk 107:59:17]} 18... Rxe1+ {[%clk 166:47:31]} 
#19. Rxe1 {[%clk 162:52:59]} 19... Qxg5 {[%clk 167:59:44]} 20. Re8+ {[%clk 167:59:15]} 20... Kh7 {[%clk 167:59:51]} 21. Qd3+ {[%clk 167:59:40]} 
#21... f5 {[%clk 167:59:50]} 22. Rf8 {[%clk 166:11:32]} 22... Bg6 {[%clk 138:15:53]} 23. Qb3 {[%clk 166:31:06]} 23... Qc1+ {[%clk 167:57:08]} 
#24. Kh2 {[%clk 133:01:31]} 24... Qc6 {[%clk 167:51:21]} 25. Qg8+ {[%clk 166:48:27]} 25... Kh6 {[%clk 167:59:45]} 26. Qh8+ {[%clk 167:58:15]} 
#26... Bh7 {[%clk 167:59:41]} 27. Rxf5 {[%clk 167:59:39]} 27... b6 {[%clk 167:59:13]} 28. g4 {[%clk 167:58:28]} 28... Nd7 {[%clk 167:59:32]} 
#29. g5+ {[%clk 167:59:11]} 29... Kg6 {[%clk 167:59:49]} 0-1\n",
#"time_control":"1/604800",
#"end_time":1693760776,
#"rated":true,
#"accuracies":{"white":73.06,"black":73.33},
#"tcn":"mC0SgvZJCJSJlB!TkA6Ebs9ziqzsjs8?px98cuENftTCehCsdkJAt3!?ks?3vM3!sA8ufeueae7Me8!3At1L89NUtrMcgpcQr!3V!?U39LXPoE5ZEMVU",
#"uuid":"cdc72474-3a1b-11ee-9ea9-25340d01000b",
#"initial_setup":"rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1",
#"fen":"r6Q/p1pn2pb/1pq3k1/5RP1/3P4/P6P/5P1K/8 w - - 1 30",
#"start_time":1691960158,
#"time_class":"daily",
#"rules":"chess",
#"white":
# {"rating":1151,
#   "result":"resigned",
#   "@id":"https://api.chess.com/pub/player/jgarnette04",
#   "username":"jgarnette04",
#   "uuid":"656d9582-c586-11e5-8008-000000000000"
# },
#"black":
#{"rating":1417,
#"result":"win",
#"@id":"https://api.chess.com/pub/player/marcussabotta",
#"username":"MarcusSabotta",
#"uuid":"54dd35d6-2aef-11dd-804d-000000000000"}}]}