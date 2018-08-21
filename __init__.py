from flask import *
import pymysql
app = Flask(__name__)
app.secret_key = "BH%7Y@5G42EN0ZRGn6wDXbbATIB!"
db = pymysql.connect("localhost","root","","ryananadb",autocommit=True)
#db = pymysql.connect(host='113.252.48.250',port=8080,user="ryanana",passwd="J8nMNJq6Fhgw3MnQ",db="ryananadb",autocommit=True)
cursor = db.cursor()

@app.route('/index')
@app.route('/')
def index():
	try:
		if session['userID'] != None: #incase user yet to login
			return redirect(url_for('adminfeedback'))
	except KeyError:
		return render_template('index.html')
	
@app.route('/main/<userid>')
def main(userid):
	return render_template('main_page.html')

@app.route('/feedback', methods = ['POST','GET'])
def feedback():
	if request.method == 'POST':
		guest = request.form["name"]
		emailreply = request.form.get("emailreply")
		callreply = request.form.get("callreply")
		smsreply = request.form.get("smsreply")
		if request.form.get("emailreply") == None:
			emailreply = "No"
		if request.form.get("callreply") == None:
			callreply = "No"
		if request.form.get("smsreply") == None:
			smsreply = "No"
	cursor.execute("INSERT INTO `feedback` (`Name`, `Content`, `Email`, `Phone`, `Email_Reply`, `Call_Reply`, `SMS_Reply`)"
				"VALUES ('"+str(request.form.get("name"))+"', '"+str(request.form.get("content"))+"', '"+str(request.form.get("email"))+"', '"+str(request.form.get("phone"))+"', '"+emailreply+"', '"+callreply+"', '"+smsreply+"');")
	return render_template('feedback.html', guest = guest)

@app.route('/admin/feedback', methods = ['POST','GET'])
def adminfeedback():
	try:
		if session['Username'] != "admin":
			return redirect(url_for('main', userid=session['userID']))
		else:
			if request.method == 'POST':
				cursor.execute("DELETE FROM `feedback` WHERE `Feedback_ID` = '"+request.form.get("Feedback_ID")+"'")
			cursor.execute("SELECT * FROM `feedback`")
			arraylist=[]
			for feedback in cursor:
				arraylist.append(feedback)
				#arraylist=[Name,Content,Email,Phone,Email_replt,Call_reply,SMS_reply]
			return render_template('admin_feedback.html',feedback = arraylist)
	except KeyError:
		return render_template('index.html')
	
@app.route('/admin/bill', methods = ['POST','GET'])
def adminbill():
	try:
		if session['Username'] != "admin":
			return redirect(url_for('main', userid=session['userID']))
		else:
			arraylist=[]
			if request.method == 'POST':
				cursor.execute("DELETE FROM `bill` WHERE `Bill_No` = '"+request.form.get("Bill_ID")+"'")
				cursor.execute("DELETE FROM `billsystem` WHERE `Bill_ID` = '"+request.form.get("Bill_ID")+"'")
			cursor.execute("SELECT * FROM `billsystem`")
			for bills in cursor.fetchall():
				cursor.execute("SELECT * FROM `bill` WHERE `Bill_No`='"+str(bills[0])+"'")
				productIDlist=[]
				total=0
				for bill in cursor.fetchall():
					cursor.execute("SELECT * FROM `market` WHERE `ProductID`='"+str(bill[2])+"'")
					for product in cursor:
						productIDlist.append(product)
						total += product[2]
				bills+=(str(total),productIDlist,)
				arraylist.append(bills)     
				#arraylist=[billNo,UserID,productIDlist]
				#productIDlist=[ProductID,ProductName,ProductPrice]
			return render_template('admin_bill.html',bills = arraylist,billslen=len(arraylist))
	except KeyError:
		return render_template('index.html')

@app.route('/login', methods = ['POST','GET'])
def login():
	try:
		if session['userID'] != None:
			return redirect(url_for('main', userid=session['userID']))
	except KeyError:
		if request.method == 'POST':
			Username = request.form.get("Username")
			Password = request.form.get("Password")
			cursor.execute("SELECT `Password` FROM `loginsystem` WHERE `Username`='"+Username+"'")
			for user in cursor:
				password = user[0]
			try:
				if Password == password:
					cursor.execute("SELECT * FROM `loginsystem` WHERE `Username`='"+request.form["Username"]+"'")
					for read_login_system in cursor:
						session['userID']=str(read_login_system[0])
						session['Username']=str(read_login_system[1])
						session['Password']=str(read_login_system[2])
						session['Phone']=str(read_login_system[3])
						session['Email']=str(read_login_system[4])
						if session['Username'] == "admin":
							return redirect(url_for('adminfeedback'))
						else:
							return redirect(url_for('main', userid=session['userID']))
				else:
					return render_template('login_page.html',result = "INCORRECT, Please Try again.")
			except UnboundLocalError:
				return render_template('login_page.html',result = "INCORRECT, Please Try again.")
		else:
			return render_template('login_page.html',result = "Please enter your correct username and password.")
					
	
@app.route('/signup')
def signup():
	cursor.execute("SELECT `Username` FROM `loginsystem`")
	arraylist=[""]
	for username in cursor:
		arraylist.append(username[0])
	return render_template('signup_page.html',usernames = json.dumps(arraylist))
	

@app.route('/signup_result', methods = ['POST','GET'])
def signup_result():
	if request.method == 'POST':
		signup_result = request.form 
		cursor.execute("INSERT INTO `loginsystem` (`Username`, `Password`,`E-mail`,`PhoneNo`)"
					"VALUES ('"+request.form["Username"]+"', '"+request.form["Password"]+"','"+request.form["Email"]+"','"+request.form["Phone"]+"');")
		cursor.execute("SELECT * FROM `loginsystem` WHERE `Username`='"+request.form["Username"]+"'")
		for read_login_system in cursor:
			session['userID']=str(read_login_system[0])
			session['Username']=str(read_login_system[1])
			session['Password']=str(read_login_system[2])
			session['Phone']=str(read_login_system[3])
			session['Email']=str(read_login_system[4])
	return render_template('signup_success.html', result = signup_result)

@app.route('/logout')
def logout():
	session.pop('userID', None)
	session.pop('Username', None)
	session.pop('Password', None)
	session.pop('Phone', None)
	session.pop('Email', None)
	session.pop('billID', None)
	return redirect(url_for('index'))
	
@app.route('/market', methods = ['POST','GET'])
def gomarket():
	try:
		if session['userID'] != None:
			if request.method == 'POST':
				cursor.execute("INSERT INTO `cart` (`User_ID`, `ProductID`) VALUES ('"+session['userID']+"', '"+request.form.get("Product_ID")+"');")
			return redirect(url_for('market',userid=session['userID']))
	except KeyError:
		return render_template('index.html')
	

@app.route('/main/market/<userid>')
def market(userid):
	cursor.execute("SELECT * FROM `market`")
	arraylist=[]
	for productlist in cursor:
		arraylist.append(productlist)
		#arraylist=[ProductID,ProductName,ProductPrice]
	return render_template('market_page.html',productlist = arraylist)

@app.route('/cart', methods = ['POST','GET'])
def gocart():
	try:
		if session['userID'] != None:
			if request.method == 'POST':
				cursor.execute("DELETE FROM `cart` WHERE `cart_ID` = '"+request.form.get("cart_ID")+"'")
			return redirect(url_for('cart',userid=session['userID']))
	except KeyError:
		return render_template('index.html')
	

@app.route('/main/cart/<userid>')
def cart(userid):
	arraylist=[]
	total = 0
	cursor.execute("SELECT * FROM `cart` WHERE `User_ID`='"+session['userID']+"'")
	for productids in cursor.fetchall():
		cursor.execute("SELECT * FROM `market` WHERE `ProductID`='"+str(productids[2])+"'")
		for product in cursor:
			product+=(str(productids[0]),)
			arraylist.append(product)
			total += product[2]
			#arraylist=[ProductName,ProductPrice,CartID]
	return render_template('cart_page.html',productlist = arraylist, total = total)

@app.route('/bill')
def gobill():
	try:
		if session['userID'] != None:
			cursor.execute("INSERT INTO `billsystem` (`Bill_ID`, `User_ID`) VALUES (NULL, '"+session['userID']+"');")
			cursor.execute("SELECT MAX(`Bill_ID`) FROM `billsystem` WHERE `User_ID`='"+session['userID']+"'")
			for billID in cursor:
				cursor.execute("SELECT * FROM `cart` WHERE `User_ID`='"+session['userID']+"'")
				for productids in cursor.fetchall():
					cursor.execute("INSERT INTO `bill` (`Bill_No`, `User_ID`,`ProductID`) VALUES ('"+str(billID[0])+"', '"+session['userID']+"','"+str(productids[2])+"');")
			session['billID']=str(billID[0])
			cursor.execute("DELETE FROM `cart` WHERE `User_ID` = '"+session['userID']+"'")
		return redirect(url_for('bill',userid=session['userID']))
	except KeyError:
		return render_template('index.html')

@app.route('/main/bill/<userid>')
def bill(userid):
	arraylist=[]
	total = 0
	cursor.execute("SELECT `ProductID` FROM `bill` WHERE `Bill_No`='"+session['billID']+"'")
	for productids in cursor.fetchall():
		cursor.execute("SELECT * FROM `market` WHERE `ProductID`='"+str(productids[0])+"'")
		for product in cursor:
			arraylist.append(product)
			total += product[2]
			#arraylist=[ProductName,ProductPrice]
	return render_template('bill_page.html',productlist = arraylist, total = total)

if __name__ == "__main__":
	app.run(debug = True)

	