from email import message


NBI_Dict = {
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