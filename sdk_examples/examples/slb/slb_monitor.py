# encoding=utf-8
import sys
import json

# 调用AcsClient参数进行身份验证
from aliyunsdkcore.client import AcsClient
# 使用阿里云官方sdk的异常处理模块
from aliyunsdkcore.acs_exception.exceptions import ServerException, ClientException
# 异常处理逻辑
from sdk_lib.exception import ExceptionHandler
# 调用创建SLB实例API
from aliyunsdkslb.request.v20140515 import CreateLoadBalancerRequest
# 调用添加默认服务器组API
from aliyunsdkslb.request.v20140515 import AddBackendServersRequest
# 调用添加TCP监听API
from aliyunsdkslb.request.v20140515 import CreateLoadBalancerTCPListenerRequest
# 调用云监控的接口查看SLB的最新监控数据
from aliyunsdkcms.request.v20180308 import QueryMetricLastRequest
# 调用云监控的接口为SLB实例创建报警规则
from aliyunsdkcms.request.v20180308 import CreateAlarmRequest
# 调用删除SLB实例API
from aliyunsdkslb.request.v20140515 import DeleteLoadBalancerRequest
# 命令行导入日志
from sdk_lib.common_util import CommonUtil

# 用户身份验证参数配置
ACS_CLIENT = AcsClient(
    'your-access-key-id',  # your-access-key-id
    'your-access-key-secret',  # your-access-key-secret
    'cn-zhangjiakou',  # your-region-id
)
# 失败重试次数
TRY_TIME = 3

'''
创建slb实例->创建tcp监听->创建后端服务器->
查询slb实例端口当前并发连接数->创建告警规则
'''


def create_load_balancer(params):
    '''
    create_load_balancer：创建slb实例
    官网API参考链接：https://help.aliyun.com/document_detail/27577.html
    '''
    try:
        # 设置创建SLB实例的调用参数
        request = CreateLoadBalancerRequest.CreateLoadBalancerRequest()
        request.set_MasterZoneId(params["master_zone_id"])
        request.set_SlaveZoneId(params["slave_zone_id"])
        request.set_LoadBalancerName(params["load_balancer_name"])
        request.set_PayType(params["pay_balancer_type"])
        # 发送调用请求并接收返回数据
        response = ACS_CLIENT.do_action_with_exception(request)
        response_json = json.loads(response)
        # 返回结果
        return response_json
    except ServerException as e:
        ExceptionHandler.server_exception(e)
    except ClientException as e:
        ExceptionHandler.client_exception(e)


def add_backend_servers(params):
    '''
    add_backend_servers：添加后端服务器
    官网API参考链接: https://help.aliyun.com/document_detail/27632.html
    '''
    counter = 0
    while counter < TRY_TIME:
        try:
            # 设置添加默认服务器组的调用参数
            request = AddBackendServersRequest.AddBackendServersRequest()
            # 负载均衡实例的ID
            request.set_LoadBalancerId(params["load_balancer_id"])
            # 要添加的后端服务器列表
            request.set_BackendServers(params["backend_servers"])
            # 发送调用请求并接收返回数据
            response = ACS_CLIENT.do_action_with_exception(request)
            response_json = json.loads(response)
            # 返回结果
            return response_json
        except ServerException as e:
            if ExceptionHandler.server_exception(e):
                return e
        except ClientException as e:
            if ExceptionHandler.client_exception(e):
                return e
        finally:
            counter += 1


def create_tcp_listener(params):
    '''
    create_tcp_listener：创建tcp监听
    官网API参考链接: https://help.aliyun.com/document_detail/27594.html
    '''
    counter = 0
    while counter < TRY_TIME:
        try:
            # 设置创建TCP监听的调用参数
            request = CreateLoadBalancerTCPListenerRequest.CreateLoadBalancerTCPListenerRequest()
            # 负载均衡实例的ID
            request.set_LoadBalancerId(params["load_balancer_id"])
            # 负载均衡实例前端使用的端口
            request.set_ListenerPort(params["listener_port"])
            # 负载均衡实例后端使用的端口
            request.set_BackendServerPort(params["backend_server_port"])
            # 监听的健康检查协议
            request.set_HealthCheckType(params["listener_health_check"])
            # 设置监听的带宽峰值
            request.set_Bandwidth(params["listener_bandwidth"])
            # 发送调用请求并接收返回数据
            response = ACS_CLIENT.do_action_with_exception(request)
            response_json = json.loads(response)
            # 返回结果
            return response_json
        except ServerException as e:
            if ExceptionHandler.server_exception(e):
                return e
        except ClientException as e:
            if ExceptionHandler.client_exception(e):
                return e
        finally:
            counter += 1


def query_metric_last(params):
    '''
    query_metric_last：查询指定监控对象的最新监控数据
    官网API参考链接: https://help.aliyun.com/document_detail/51939.html
    '''
    counter = 0
    while counter < TRY_TIME:
        try:
            request = QueryMetricLastRequest.QueryMetricLastRequest()
            # 名字空间，表明监控数据所属产品
            request.set_Project(params["project"])
            # 监控项名称
            request.set_Metric(params["metric_name"])
            # 过滤项
            request.set_Dimensions(params['dimensions'])
            response = ACS_CLIENT.do_action_with_exception(request)
            response_json = json.loads(response)
            return response_json
        except ServerException as e:
            ExceptionHandler.server_exception(e)
        except ClientException as e:
            ExceptionHandler.client_exception(e)
        finally:
            counter += 1


def create_alarm(params):
    '''
    create_alarm：创建报警规则，可以为某一个实例创建报警规则，也可以为多个实例同时创建报警规则
    官网API参考链接: https://help.aliyun.com/document_detail/51910.html
    '''
    counter = 0
    while counter < TRY_TIME:
        try:
            request = CreateAlarmRequest.CreateAlarmRequest()

            # 产品名称，参考各产品对应的project
            request.set_Namespace(params["name_space"])
            # 报警规则名称
            request.set_Name(params["name"])
            # 相应产品对应的监控项名称，参考各产品metric定义
            request.set_MetricName(params["metric_name"])
            # 报警规则对应实例列表
            request.set_Dimensions(params["dimensions"])
            # 统计方法，必须与定义的metric一致
            request.set_Statistics(params["statistics"])
            # 报警比较符
            request.set_ComparisonOperator(params["comparison_operator"])
            # 报警阈值，目前只开放数值类型功能
            request.set_Threshold(params["threshold"])
            response = ACS_CLIENT.do_action_with_exception(request)
            response_json = json.loads(response)
            return response_json
        except ServerException as e:
            ExceptionHandler.server_exception(e)
        except ClientException as e:
            ExceptionHandler.client_exception(e)
        finally:
            counter += 1


def delete_load_balancer(load_balancer_id):
    '''
    delete_load_balancer：删除slb实例
    官网API参考链接：https://help.aliyun.com/document_detail/27579.html
    '''
    try:
        # 设置删除SLB实例的调用参数
        request = DeleteLoadBalancerRequest.DeleteLoadBalancerRequest()
        # 负载均衡实例的ID
        request.set_LoadBalancerId(load_balancer_id)
        # 发送调用请求并接收返回数据
        response = ACS_CLIENT.do_action_with_exception(request)
        response_json = json.loads(response)
        # 返回结果
        return response_json
    except ServerException as e:
        ExceptionHandler.server_exception(e)
    except ClientException as e:
        ExceptionHandler.client_exception(e)


def main():
    params = {}
    # 设置创建SLB实例的参数
    # 设置新建SLB实例的主可用区为cn-zhangjiakou-a
    params["master_zone_id"] = "cn-zhangjiakou-a"
    # 设置新建SLB实例的主可用区为cn-zhangjiakou-b
    params["slave_zone_id"] = "cn-zhangjiakou-b"
    # 设置新建SLB实例的名称为SLB1
    params["load_balancer_name"] = "SLB1"
    # 设置新建SLB实例的计费类型为按量计费
    params["pay_balancer_type"] = "PayOnDemand"

    # 设置添加到默认服务器组的ECS的实例ID和权重
    params["backend_servers"] = [{"ServerId": "i-8vbe8xxxxxxxxxxxw", "Weight": "100"},
                                 {"ServerId": "i-8vbe8yixxxxxxxxxxxxv", "Weight": "100"}]

    # 设置添加TCP监听的参数
    # 前端使用的端口为80
    params["listener_port"] = 80
    # 后端服务器开放用来接收请求的端口为80
    params["backend_server_port"] = 80
    # 健康检查协议为TCP
    params["listener_health_check"] = "tcp"
    # TCP监听的带宽峰值为-1，即不限制带宽峰值
    params["listener_bandwidth"] = -1

    # 设置查询监控项的参数
    # 设置监控数据所属产品
    params["project"] = "acs_slb_dashboard"
    # 设置监控项名称
    params["traffic_tx_new"] = "InstanceQpsUtilization"

    # 设置创建告警的参数
    # 设置告警规则所属产品
    params["name_space"] = "acs_slb_dashboard"
    # 设置告警规则名称
    params["name"] = "slb_alarm"
    # 设置告警中SLB对应的监控项名称
    params["metric_name"] = "InstanceQpsUtilization"
    # 设置统计方法
    params["statistics"] = "Average"
    # 设置报警比较符
    params["comparison_operator"] = ">="
    # 设置报警阈值
    params["threshold"] = 35

    # 创建slb实例
    # 获取create_load_balancer函数返回值，load_balancer_json为结果的json串
    load_balancer_json = create_load_balancer(params)
    # 打印 load_balancer_json结果，其中"create_load_balancer"是对json串起的名字
    CommonUtil.log("create_load_balancer", load_balancer_json)

    # slb实例id
    params["load_balancer_id"] = load_balancer_json["LoadBalancerId"]

    # 创建tcp监听
    result_json = create_tcp_listener(params)
    CommonUtil.log("create_tcp_listener", result_json)

    # 创建后端服务器
    result_json = add_backend_servers(params)
    CommonUtil.log("add_backend_servers", result_json)

    # 查询slb实例QPS使用率
    params["dimensions"] = '[{"instanceId":"' + load_balancer_json["LoadBalancerId"] + '"}]'
    result_json = query_metric_last(params)
    CommonUtil.log("query_metric_last", result_json)

    # 创建告警规则
    params["metric_name"] = "InstanceQpsUtilization"
    result_json = create_alarm(params)
    CommonUtil.log("create_alarm", result_json)

    # 删除slb实例
    # 删除返回的LoadBalancerId对应的SLB实例
    load_balancer_json = delete_load_balancer(load_balancer_json["LoadBalancerId"])
    # 打印 load_balancer_json结果
    CommonUtil.log("delete_load_balancer", load_balancer_json)


if __name__ == "__main__":
    sys.exit(main())