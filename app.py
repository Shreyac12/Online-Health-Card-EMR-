from flask import Flask, render_template, request, redirect, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, login_manager, logout_user,LoginManager,login_required,current_user
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SubmitField
from wtforms.validators import InputRequired, Length


app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:123456@localhost/HMS'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = 'False'
app.config['SECRET_KEY'] = 'secret'

db = SQLAlchemy(app)


login_manager = LoginManager(app)
login_manager.login_view = "login"


@login_manager.user_loader
def loaduser(user_id):
    return Patient.query.get(int(user_id))

@login_manager.user_loader
def loaduser(user_id):
    return Doctor.query.get(int(user_id))


# patient visits the hospital
Visit = db.Table('Visit',
                 db.Column('Patient_id', db.Integer,
                           db.ForeignKey('patient.id')),
                 db.Column('Hospital_id', db.Integer,
                           db.ForeignKey('hospital.id'))
                 )


# doctor treats the patient
Treat = db.Table('Treat',
                 db.Column('Patient_id', db.Integer,
                           db.ForeignKey('patient.id')),
                 db.Column('Hospital_id', db.Integer,
                           db.ForeignKey('doctor.id'))
                 )


class Hospital(db.Model):
    id = db.Column(db.Integer, db.Sequence(
        'seq_reg_id', start=1, increment=1), primary_key=True)
    hname = db.Column(db.String(50), nullable=False, unique=True)
    haddress = db.Column(db.String(50), nullable=False)
    city = db.Column(db.String(50), nullable=False)
    h_ref = db.relationship('Doctor', backref='hospital')
    h1_ref = db.relationship('Patient', secondary=Visit, backref='hospital')

    def __init__(self, hname, haddress, city):
        self.hname = hname
        self.haddress = haddress
        self.city = city


class Patient(db.Model, UserMixin):
    id = db.Column(db.Integer, db.Sequence(
        'seq_reg_id', start=1, increment=1), primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    gender = db.Column(db.String(50), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    phno = db.Column(db.String(50), nullable=False, unique=True)
    address = db.Column(db.String(50), nullable=False)
    p_ref = db.relationship('Medicalrecord', backref='patient')
    p1_ref = db.relationship('Appointment', backref='patient')
    h1_ref = db.relationship('Doctor', secondary=Treat, backref='patient')

    def __init__(self, name, gender, age, phno, address):
        self.name = name
        self.gender = gender
        self.age = age
        self.phno = phno
        self.address = address


class Doctor(db.Model,UserMixin):
    id = db.Column(db.Integer, db.Sequence(
        'seq_reg_id', start=1, increment=1), primary_key=True)
    dname = db.Column(db.String(50), nullable=False)
    gender = db.Column(db.String(50), nullable=False)
    specialization = db.Column(db.String(50), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    phno = db.Column(db.String(50), nullable=False)
    d1_ref = db.relationship('Appointment', backref='doctor')
    fd_hid = db.Column(db.Integer, db.ForeignKey('hospital.id'))

    def __init__(self, dname, gender, specialization, age, phno, fd_hid):
        self.dname = dname
        self.gender = gender
        self.specialization = specialization
        self.age = age
        self.phno = phno
        self.fd_hid = fd_hid


class Medicalrecord(db.Model):
    mrid = db.Column(db.Integer, db.Sequence(
        'seq_reg_id', start=1, increment=1), primary_key=True)
    date = db.Column(db.String(50), nullable=True)
    disease = db.Column(db.String(50), nullable=True)
    drugs = db.Column(db.String(50), nullable=True)
    diagnosis = db.Column(db.String(50), nullable=True)
    fm_pid = db.Column(db.Integer, db.ForeignKey('patient.id'))

    def __init__(self, drugs, date, disease, diagnosis, fm_pid):
        self.drugs = drugs
        self.date = date
        self.disease = disease
        self.diagnosis = diagnosis
        self.fm_pid = fm_pid


class Appointment(db.Model):
    apptid = db.Column(db.Integer, db.Sequence(
        'seq_reg_id', start=1, increment=1), primary_key=True)
    time = db.Column(db.String(50), nullable=False)
    date = db.Column(db.String(50), nullable=False)
    fa_pid = db.Column(db.Integer, db.ForeignKey('patient.id'))
    fa_did = db.Column(db.Integer, db.ForeignKey('doctor.id'))

    def __init__(self, date, time, fa_pid, fa_did):
        self.time = time
        self.date = date
        self.fa_pid = fa_pid
        self.fa_did = fa_did



class RegistrationForm(FlaskForm):
    name = StringField(validators=[InputRequired()], render_kw={"placeholder": "name"})

    gender = StringField(validators=[InputRequired(), Length(
        min=4, max=10)], render_kw={"placeholder": "gender"})

    age = IntegerField(validators=[InputRequired()], render_kw={"placeholder": "age"})

    phno = StringField(validators=[InputRequired(), Length(
        min=10, max=10)], render_kw={"placeholder": "Phone number"})

    address = StringField(validators=[InputRequired(), Length(
        min=4, max=10)], render_kw={"placeholder": "address"})
    
    submit = SubmitField("REGISTER")

# __________________________________________________________________

@app.route('/dhome')
def dhome():
    return render_template('dhome.html')



@app.route('/phome')
def phome():
    return render_template('phome.html')


# ___________logins____________

@app.route('/', methods=['POST', 'GET'])
def home():
    if request.method=='POST':
        id=request.form.get('id')
        name=request.form.get('name')
        phno=request.form.get('phno')
        checkpatient=Patient.query.filter_by(id=id,name=name,phno=phno).first()
        if checkpatient:
            login_user(checkpatient)
            return render_template('phome.html')     
        id=request.form.get('id')
        dname=request.form.get('dname')
        phno=request.form.get('phno')
        checkdoctor=Doctor.query.filter_by(dname=dname,phno=phno,id=id).first()
        if checkdoctor:
            login_user(checkdoctor)
            return redirect('/dhome')
        if not checkdoctor or checkpatient:
            flash('The account doesnt exist')
            return render_template('home10.html')
    return render_template('home10.html')



@app.route('/login', methods=['POST', 'GET'])
def dlogin():
    if request.method=='POST':
        id=request.form.get('id')
        dname=request.form.get('dname')
        phno=request.form.get('phno')
        checkdoctor=Doctor.query.filter_by(dname=dname,phno=phno,id=id).first()
        if checkdoctor:
            login_user(checkdoctor)
            return render_template('dhome.html',doctorname=current_user.dname)
        else:
            flash('The account doesnt exist')
            return render_template('dlogin.html')
    return render_template('dlogin.html')


@app.route('/plogin', methods=['POST', 'GET'])
def login():
    if request.method=='POST':
        id=request.form.get('id')
        name=request.form.get('name')
        phno=request.form.get('phno')
        checkpatient=Patient.query.filter_by(id=id,name=name,phno=phno).first()
        if checkpatient:
            login_user(checkpatient)
            return render_template('phome.html',patientname=current_user.name)
        else:
            flash('the account doesnt exist')
    return render_template('plogin.html')

# ________end login____________


# __________register______________

@app.route('/pregister', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()

    if form.validate_on_submit() and request.method=='POST':
        newuser = Patient(name=form.name.data,gender=form.gender.data,age=form.age.data,phno=form.phno.data,address=form.address.data)
        checkuser = Patient.query.filter_by(phno=form.phno.data).first()
        if not checkuser:
            db.session.add(newuser)
            db.session.commit()
            return redirect('/plogin')
        if checkuser:
            flash('the user already exists')
    return render_template('pregister.html', form=form)


@app.route('/dregister', methods=['POST', 'GET'])
def dregister():
    
    if request.method=='POST':
        dname=request.form['dname']
        gender=request.form['gender']
        specialization=request.form['specialization']
        age=request.form['age']
        phno=request.form['phno']
        fd_hid=request.form['fd_hid']
        doc=Doctor(dname,gender,specialization,age,phno,fd_hid)    
        query=Doctor.query.filter_by(phno=phno,dname=dname).first()
        if not query:    
            db.session.add(doc)
            db.session.commit()
        else:
            flash('the account already exists')

        return redirect('/login')
    return render_template('dregister.html')


# ______________hospital_____________


@app.route('/dochospital')
def dochospital():
        query = Hospital.query.all()
        return render_template('dochospital10.html',query=query)


@app.route('/docchoosedoc/<id>', methods=['POST', 'GET'])
# @login_required
def docchoosedoc(id):
        
        if request.method=='POST':
            dname=request.form['dname']
            gender=request.form['gender']
            specialization=request.form['specialization']
            age=request.form['age']
            phno=request.form['phno']
            fd_hid=request.form['fd_hid']
            doc=Doctor(dname,gender,specialization,age,phno,fd_hid)    
            querys=Doctor.query.filter_by(phno=phno).first()
            
            if not querys:    
                db.session.add(doc)
                db.session.commit()
                query = db.engine.execute(f"SELECT * FROM `Doctor` WHERE fd_hid={fd_hid}")
                return render_template('docchoosedoc10.html',query=query)
            else:
                flash('the account already exists')
                query = db.engine.execute(f"SELECT * FROM `Doctor` WHERE fd_hid={fd_hid}")
                return render_template('docchoosedoc10.html',query=query)

        query = db.engine.execute(f"SELECT * FROM `Doctor` WHERE fd_hid={id}")
        return render_template('docchoosedoc10.html',query=query,id=id)




# ____________hospital end________________

# _________________doctor__________________  


@app.route('/dprofile',methods=['POST','GET'])
def dprofile():
    em=current_user.id
    query=db.engine.execute(f"SELECT * FROM  `Doctor` WHERE doctor.id={em}")
    item=Doctor.query.filter_by(id=em).first()
    if request.method=='POST':
        dname=request.form['dname']
        gender=request.form['gender']
        specialization=request.form['specialization']
        age=request.form['age']
        phno=request.form['phno']
        fd_hid=request.form['fd_hid']
        db.engine.execute(f"UPDATE `Doctor` SET `dname`='{dname}',`gender`='{gender}',`specialization`='{specialization}',`age`='{age}',`phno`='{phno}',`fd_hid`='{fd_hid}' WHERE id={em}")
        db.session.commit()
        flash('details updated')
        return redirect('/dprofile')
    return render_template('dprofile10.html', query=query,item=item)


@app.route('/ddelete/<int:id>',methods=['POST','GET'])
def delete(id):
    db.engine.execute(f"DELETE FROM `Doctor` WHERE doctor.id={id}")
    flash('data deleted')
    return redirect('/')


@app.route('/appointments')
def appointments():
    if Doctor.is_authenticated:
        doctorid=current_user.id
        query=db.engine.execute(f"SELECT appointment.*,patient.id,patient.name FROM `Appointment`,`Patient`,`Doctor` WHERE appointment.fa_pid=patient.id AND appointment.fa_did=doctor.id AND `fa_did`={doctorid}")
        return render_template('bookinghistory.html',query=query,doctorname=current_user.dname)




@app.route('/patientrecord', methods=['POST', 'GET'])
def patientrecord():
    id=request.form.get('id')
    checkpatient=Patient.query.filter_by(id=id).first()
    if checkpatient:
        login_user(checkpatient)
        query=db.engine.execute(f"SELECT DISTINCT * FROM `Patient`,`Medicalrecord` WHERE fm_pid=patient.id AND fm_pid={id}")
        return render_template('patientrecord10.html',query=query)
    if request.method=='POST':
        date=request.form.get('date')
        disease=request.form.get('disease')
        drugs=request.form.get('drugs')
        diagnosis=request.form.get('diagnosis')
        fm_pid=request.form.get('fm_pid')
        patrec=Medicalrecord(date,disease,drugs,diagnosis,fm_pid)
        db.session.add(patrec)
        db.session.commit()
        checkpatients=Patient.query.filter_by(id=fm_pid).first()
        if checkpatients:
            query=db.engine.execute(f"SELECT DISTINCT * FROM `Patient`,`Medicalrecord` WHERE fm_pid=patient.id AND fm_pid={fm_pid}")
            return render_template('patientrecord10.html',query=query)
        if not checkpatients:
            flash('Invalid Patient ID')
    return render_template('patientrecord10.html')        


# ____________doctor end_________________

# ______________patient________________


@app.route('/pprofile',methods=['POST','GET'])
def pprofile():
    em=current_user.id
    query=db.engine.execute(f"SELECT * FROM  `Patient` WHERE patient.id={em}")
    item=Patient.query.filter_by(id=em).first()
    if request.method=='POST':
        name=request.form['name']
        gender=request.form['gender']
        age=request.form['age']
        phno=request.form['phno']
        address=request.form['address']
        db.engine.execute(f"UPDATE `Patient` SET `name`='{name}',`gender`='{gender}',`age`='{age}',`phno`='{phno}',`address`='{address}' WHERE id={em}")
        db.session.commit()
        flash('details updated')
        return redirect('/pprofile')
    return render_template('pprofile10.html', query=query,item=item)


@app.route('/pdelete/<int:id>',methods=['POST','GET'])
def pdelete(id):
    db.engine.execute(f"DELETE FROM `Doctor` WHERE doctor.id={id}")
    flash('data deleted')
    return redirect('/')


@app.route('/hospital')
def hospital():
    if not Patient.is_authenticated:
        return redirect('/plogin')
    else:
        query = Hospital.query.all()
        return render_template('hospital.html', query=query)
    

@app.route('/choosedoc/<int:id>', methods=['POST', 'GET'])
# @login_required
def choosedoc(id):
    if not Patient.is_authenticated:
        return redirect('/plogin')
    else:
        query = db.engine.execute(f"SELECT * FROM `Doctor` where fd_hid={id}")
        return render_template('choosedoc.html', query=query,patient=current_user.id)



@app.route('/book/<id>', methods=['POST', 'GET'])
@login_required
def book(id):
    if request.method == 'POST':
        time = request.form['time']
        date = request.form['date'] 
        fa_pid = request.form['fa_pid']
        fa_did=request.form['fa_did'] 
        appt=Appointment(time,date,fa_pid,fa_did)
        db.session.add(appt)
        db.session.commit()
        return redirect('/history')
        
    return render_template('book.html',id=id,patient=current_user.id)


@app.route('/history')
def history():
    if Patient.is_authenticated:
        patientid=current_user.id
        query=db.engine.execute(f"SELECT appointment.*,doctor.dname,doctor.specialization,hospital.hname FROM `Appointment`,`Doctor`,`Hospital` WHERE appointment.fa_did=doctor.id AND doctor.fd_hid=hospital.id AND `fa_pid`={patientid}")
        return render_template('history.html',query=query)
    else:
        flash('please login')


@app.route('/medical',methods=['POST','GET'])
def medical():
    patientid=current_user.id
    query=db.engine.execute(f"SELECT * FROM `Medicalrecord`,`Patient` WHERE fm_pid=patient.id AND medicalrecord.fm_pid={patientid}")
    return render_template('patmeds.html',query=query)

# _____________patient end__________________

@app.route('/logout', methods=['POST', 'GET'])
@login_required
def logout():
    logout_user()
    return redirect('/')


@app.route('/logout', methods=['POST', 'GET'])
@login_required
def dlogout():
    logout_user()
    return redirect('/')


if __name__ == "__main__":
    app.run(debug=True)