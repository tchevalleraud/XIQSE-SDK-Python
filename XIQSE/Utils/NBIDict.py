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