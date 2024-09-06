from faker import Faker
from models import db, DefaultReason, DefaultApplication, Customer, DefaultRebirth
from app import create_app

app = create_app()

fake = Faker()

def create_fake_customers(n):
    industries = [
        '金融', '技术', '医疗', '教育', '制造业',
        '零售', '能源', '公用事业', '交通运输', '电信'
    ]
    provinces = [
        '北京', '上海', '广东', '浙江', '江苏',
        '四川', '湖南', '湖北', '山东', '河南'
    ]
    credit_ratings = ['A', 'B', 'C', 'D']
    external_ratings = ['A', 'B', 'C', 'D']
    
    with app.app_context():
        for _ in range(n):
            customer = Customer(
                customer_name=fake.company(),
                username=fake.unique.random_int(min=100000, max=999999),
                password=fake.password(),
                status=fake.random_element([0, 1]),
                industry_classification=fake.random_element(industries),
                region_classification=fake.random_element(provinces),
                credit_rating=fake.random_element(credit_ratings),
                group=fake.company_suffix(),
                external_rating=fake.random_element(external_ratings)
            )
            db.session.add(customer)
        db.session.commit()

def create_fake_default_reasons():
    reasons = [
        "6个月内，交易对手技术性或资金等原因，给当天结算带来头寸缺口2次以上",
        "6个月内因各种原因导致成交后撤单2次以上",
        "未能按照合约规定支付或延期支付利息、本金或其他交付义务（不包括在宽限期内延期支付）",
        "关联违约：如果集团（内部联系较紧密的集团）或集团内任一公司（较重要的子公司，一旦发生违约会对整个集团造成较大影响的）发生违约，可视情况作为集团内所有成员违约的触发条件",
        "发生消极债务置换：债务人提供给债权人新的或重组的债务，或新的证券组合、现金或资产低于原有金融义务；或为了债务人未来避免发生破产或拖欠还款而进行的展期或重组",
        "申请破产保护，发生法律接管，或者处于类似的破产保护状态",
        "在其他金融机构违约（包括不限于：人行征信记录中显示贷款分类状态不良类情况，逾期超过90天等），或外部评级显示为违约级别"
    ]
    with app.app_context():
        for reason in reasons:
            db.session.add(DefaultReason(reason=reason, is_enabled=True))
        db.session.commit()

def create_fake_default_applications(n):
    with app.app_context():
        customers = Customer.query.all()
        for _ in range(n):
            application_time = fake.date_time_this_year()
            audit_status = fake.random_element([0, 1, 2])
            
            # 如果审核状态为0，审核时间为空
            audit_data = None
            if audit_status in [1, 2]:
                # 如果审核状态为1或2，审核时间应晚于申请时间
                audit_data = fake.date_time_between(start_date=application_time, end_date='+1y')

            default_application = DefaultApplication(
                customer_id=fake.random_element([c.customer_id for c in customers]),
                audit_status=audit_status,
                severity=fake.random_element(['高', '中', '低']),
                uploaduser_id=fake.random_int(min=1, max=100),
                application_time=application_time,
                audit_data=audit_data,
                remarks=fake.text(),
                default_status=fake.random_element([0, 1])  # 默认为0，只有在重生成功时才会设为1
            )
            db.session.add(default_application)
        db.session.commit()

def create_fake_default_rebirths(n):
    with app.app_context():
        default_apps = DefaultApplication.query.all()
        customers = Customer.query.all()
        for _ in range(n):
            default_application = fake.random_element(default_apps)
            rebirth_status = fake.random_element([0, 1, 2])  # 0进行中，1同意，2拒绝
            
            # 只有在审核状态为1时，才会把违约记录标记为重生
            if rebirth_status == 1:
                default_application.default_status = 1
                db.session.add(default_application)

            rebirth = DefaultRebirth(
                customer_id=default_application.customer_id,
                default_id=default_application.id,
                audit_status=rebirth_status,
                remarks=fake.text()
            )
            db.session.add(rebirth)
        db.session.commit()

# 调用函数以生成数据
create_fake_customers(100)
create_fake_default_reasons()
create_fake_default_applications(100)
create_fake_default_rebirths(100)