#!
echo "initを開始"
sudo rm -r RangeBot/
sudo rm -r avgbot_app/
python3 -m venv avgbot_app/env
source ~/avgbot_app/env/bin/activate
pip install pip --upgrade
git clone https://github.com/shoo5123/RangeBot.git
pip install python-binance
nohup python3 /home/ec2-user/RangeBot/Range/range.py &
echo "init処理が終了"