from flask import Blueprint, request, send_file, jsonify, Flask, render_template
from models import db, DefaultApplication,Customer,DefaultRebirth
import os
from datetime import datetime

main = Blueprint('main', __name__)

#注册
@main.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    customer_name = data.get('customer_name') 
    username = data.get('username')
    password = data.get('password')
    industry_classification = data.get('industry_classification')
    region_classification = data.get('region_classification')
    credit_rating = data.get('credit_rating')
    group = data.get('group')
    external_rating = data.get('external_rating')

    #以下内容必填
    if not customer_name or not username or not password or not industry_classification or not region_classification or not external_rating:
        return jsonify({'code': 400, 'message': 'Missing fields'}), 400

    if Customer.query.filter_by(username=username).first():
        return jsonify({'code': 400, 'message': 'User already exists'}), 400

    customer = Customer(
        customer_name = customer_name,
        username=username,
        password = password,
        status = 0,#初始状态为“正常”
        industry_classification = industry_classification,
        region_classification = region_classification,
        credit_rating = credit_rating,
        group = group,
        external_rating = external_rating
        )
    db.session.add(customer)
    db.session.commit()

    return jsonify({'code': 200, 'message': 'User registered successfully'}), 200

#登录
@main.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    customer = Customer.query.filter_by(username=username).first()

    if customer is None or customer.password != password:
        return jsonify({'message': 'Invalid username or password', 'code': 400}), 400

    return jsonify({'message': 'Login successful', 'code': 200}), 200


#3.1违约原因维护
@main.route('/default_reasons',methods=['GET','POST'])
def manage_default_reasons():
    if request.method == 'POST':
        #获取请求中的数据
        data =request.get_json()
        reason = data.get('reason')
        is_enable = data.get('is_enabled')
        order = data.get('order')

        #数据验证和处理
        #这里假设有一个DefaultReason模型来存储违约原因数据
        #添加到数据库并提交
        #返回响应
        return jsonify({'message':'违约原因已添加'}), 201
    else:
        #返回所有违约原因
        reasons = []
        return jsonify(reason), 200
    
# 3.2 违约认定申请
@main.route('/default_applications', methods=['GET', 'POST'])
def default_applications():
    if request.method == 'POST':
        data = request.get_json()
        customer_id = data.get('customer_id')
        severity = data.get('severity')
        remarks = data.get('remarks')

        uploaduser_id = data.get('uploaduser_id')

        # 限制约定
        # 业务逻辑：检查必填项
        if not customer_id or not remarks:
            return jsonify({'message': '客户名称和违约原因是必填项'}), 400
        
        # 业务逻辑：检查认定者是否是违约者
        customer = Customer.query.filter_by(customer_id=uploaduser_id).first()
        #认定者不存在
        if  not customer:
            return jsonify({'message':'客户不存在'}),404
        #认定者是违约者
        if customer.status == 1:
            return jsonify({'message':'认定人是违约客户，无法申请'}),400
        
        application = DefaultApplication(
            customer_id = customer_id,
            audit_status = 0,#初始状态为‘进行中’
            severity = severity,
            uploaduser_id = uploaduser_id,
            application_time = datetime.now(),
            remarks = remarks,
            default_status = 0 #初始状态为“正常”
        )
        db.session.add(application)
        db.session.commit()

        return jsonify({'message': '违约认定申请已创建'}), 201
    else:
        #可有可无
        # 返回所有违约认定申请
        applications = DefaultApplication.query.all()
        return jsonify([{
            'id': app.id,
            'customer_id': app.customer_id,
            'audit_status': app.audit_status,
            'severity': app.severity,
            'upload_user': app.upload_user,
            'application_time': app.application_time,
            'audit_data': app.audit_data,
            'remarks': app.remarks,
            'default_status': app.default_status
        } for app in applications]), 200

# 3.3 违约认定审核
@main.route('/default_applications/<int:id>/review', methods=['PUT'])
def review_default_application(id):
    data = request.get_json()
    audit_status = data.get('audit_status')

    if audit_status == 0:
        return jsonify({'message': '审核发生错误'}), 201
    
    # 查找违约申请记录
    application = DefaultApplication.query.get_or_404(id)

    # 更新审核状态
    application.audit_status = audit_status
    application.audit_data = datetime.datetime.now()
    db.session.commit()

    #查找违约用户
    customer = Customer.query.get(application.customer_id)

   # 判断用户状态
    if audit_status == 1:
        #更新用户状态为“冻结”
        customer.status = 1
        db.session.commit()
    elif audit_status == 2:
        #查找违约用户是否有违约记录
        existing_defaults = DefaultApplication.query.filter_by(customer_id=application.customer_id, audit_status=1).count()
        if existing_defaults > 0:
            #更新用户状态为“冻结”
            customer.status = 1
        else:
            #更新用户状态为“正常”
            customer.status = 0

    return jsonify({'message': '违约认定审核已更新'}), 200


# 3.4 违约信息查询
@main.route('/default_applications/search', methods=['GET'])
def search_default_applications():
    customer_name = request.args.get('customer_name')

    if not customer_name:
        return jsonify({'message': '请输入用户名称'}), 404
    else:
        # 查找客户是否存在
        customer_exists = db.session.query(Customer).filter(Customer.customer_name == customer_name).first()
        if not customer_exists:
            return jsonify({'message': '无该用户'}), 201
        else:
            # 创建查询
            query = query.join(DefaultApplication, Customer, DefaultApplication.customer_id == Customer.customer_id)
            #查询有没有违约信息
            query = query.filter(Customer.customer_name == customer_name)
            if query.count() == 0:
                return jsonify({'message': '无违约信息'}), 201
            else:
                applications = query.all()

                return jsonify([{
                    'id': app.id,
                    'customer_id': app.customer_id,
                    'audit_status': app.audit_status,
                    'severity': app.severity,
                    'uploaduser_id': app.uploaduser_id,
                    'application_time': app.application_time,
                    'audit_data': app.audit_data,
                    'remarks': app.remarks,
                    'default_status': app.default_status
                } for app in applications]), 200

# 3.5 违约重生
@main.route('/default_rebirths', methods=['POST'])
def rebirth_default():
    data = request.get_json()
    customer_id = data.get('customer_id')
    default_id = data.get('default_id')
    remarks = data.get('remarks')

    # 创建违约重生记录
    rebirth = DefaultRebirth(
        customer_id=customer_id,
        default_id=default_id,
        audit_status=0,  # 初始状态为"进行中"
        remarks=remarks
    )
    db.session.add(rebirth)
    db.session.commit()

    return jsonify({'message': '违约重生申请已创建'}), 201


# 3.6 违约重生审核
@main.route('/default_rebirths/<int:id>/review', methods=['PUT'])
def review_default_rebirth(id):
    data = request.get_json()
    audit_status = data.get('audit_status')

    # 查找违约重生记录
    rebirth = DefaultRebirth.query.get_or_404(id)

    # 更新审核状态
    rebirth.audit_status = audit_status
    db.session.commit()

    return jsonify({'message': '违约重生审核已更新'}), 200

# 3.7 违约统计
@main.route('/statistics/industry', methods=['GET'])
def industry_statistics():
    # 查询和计算行业统计数据
    industry_stats = db.session.query(
        Customer.industry_classification,
        db.func.count(Customer.customer_id)
    ).filter(Customer.status == 1) \
    .group_by(Customer.industry_classification).all()

    statistics = [
        {
            'industry': industry,
            'default_count': count
        }
        for industry, count in industry_stats
    ]

    return jsonify(statistics), 200

@main.route('/statistics/region', methods=['GET'])
def region_statistics():
    # 查询和计算区域统计数据
    region_stats = db.session.query(
        Customer.region_classification,
        db.func.count(Customer.customer_id)
    ).filter(Customer.status == 1) \
    .group_by(Customer.region_classification).all()

    # Prepare the result
    statistics = [
        {
            'region': region,
            'default_count': count
        }
        for region, count in region_stats
    ]

    return jsonify(statistics), 200

@main.route('/statistics', methods=['GET'])
def statistics_page():
    return render_template('statistics.html')