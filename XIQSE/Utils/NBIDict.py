from email import message


NBI_Dict = {
    'configureDiscoveredDevice': {
        'json': '''
            mutation {
                network {
                    configureDiscoveredDevice(input: {
                        deviceConfig: {
                            generalConfig: {
                                adminProfile: "<PROFILE>"
                                defaultSitePath: "<SITEPATH>"
                                sysName: "<SYSNAME>"
                            }
                            serialNumber: "<SERIALNUMBER>"
                            ztpPlusConfig: {
                                dnsServer: "<DNSSERVER1>"
                                dnsServer2: "<DNSSERVER2>"
                                gatewayAddress: "<GATEWAY>"
                                useDiscoveredMode: INTERFACE
                                subnetAddress: "<SUBNET>"
                            }
                        }
                    }) {
                        message
                        status
                    }
                }
            }
        '''
    },
    'createDevice': {
        'json': '''
            mutation {
                network {
                    createDevices(input: {
                        devices: {
                            ipAddress: "<IP>"
                            siteLocation: "<SITEPATH>"
                            profileNAme: "<PROFILE>"
                        }
                    }) {
                        message
                        status
                    }
                }
            }
        '''
    },
    'createSitePath': {
        'json': '''
            mutation {
                network {
                    createSite(input: {
                        siteLocation: "<SITEPATH>",
                        siteConfig: {
                            actionsConfig: {
                                addSyslogReceiver: true
                                addTrapReceiver: true
                                autoAddDevices: true
                                addToArchive: true
                            }
                            customActionsConfig: {
                                mutationType: REMOVE_ALL
                            }
                        }
                    }) {
                        message
                        status
                    }
                }
            }
        '''
    },
    'deleteDevice': {
        'json': '''
            mutation {
                network {
                    deleteDevices(input: {
                        devices: [
                            {
                                ipAddress: "<IP>"
                            }
                        ]
                        removeData: true
                    }) {
                        message
                        status
                    }
                }
            }
        '''
    },
    'executeWorkflow': {
        'json': '''
            mutation {
                workflows {
                    startWorkflow(input:{
                        path: "<WORKFLOWPATH>",
                        variables: "<VARIABLES>"
                    }) {
                        errorCode
                        executionId
                        message
                        status
                    }
                }
            }
        ''',
        'key': 'executionId'
    },
    'nbiAccess': {
        'json': '''
            query {
                administration {
                    serverInfo {
                        version
                    }
                }
            }
        ''',
        'key': 'version'
    }
}