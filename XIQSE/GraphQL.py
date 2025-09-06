import json
import time

class GraphQL(object):
    def __init__(self, context):
        self.ctx = context
    
    def test(self):
        self.ctx.log("XIQSE.GraphQL.test => OK")
    
    def nbiQuery(self, query, variables=None, timeout=30):
        """
        Execute a GraphQL query using the NBI (North Bound Interface)
        
        Args:
            query (str): The GraphQL query string
            variables (dict, optional): Variables for the query
            timeout (int, optional): Timeout in seconds (default: 30)
            
        Returns:
            dict: The response data from the GraphQL query
            
        Raises:
            RuntimeError: If the query fails or times out
        """
        try:
            self.ctx.debug("Executing GraphQL query: {}", query[:100] + "..." if len(query) > 100 else query)
            
            if variables:
                self.ctx.debug("Query variables: {}", json.dumps(variables, indent=2))
            
            # Prepare the request payload
            payload = {
                "query": query
            }
            
            if variables:
                payload["variables"] = variables
            
            # Execute the query using emc_nbi
            start_time = time.time()
            response = self.ctx.emc_nbi.query(payload, timeout=timeout)
            execution_time = time.time() - start_time
            
            self.ctx.debug("GraphQL query executed in {:.2f} seconds", execution_time)
            
            # Check for errors in the response
            if "errors" in response and response["errors"]:
                error_msg = "GraphQL query errors: {}".format(json.dumps(response["errors"], indent=2))
                self.ctx.error(error_msg)
                raise RuntimeError(error_msg)
            
            # Log successful response
            if "data" in response:
                self.ctx.debug("GraphQL query successful, data keys: {}", list(response["data"].keys()) if response["data"] else "None")
            
            return response
            
        except Exception as e:
            error_msg = "GraphQL query failed: {}".format(str(e))
            self.ctx.error(error_msg)
            raise RuntimeError(error_msg)
    
    def nbiMutation(self, mutation, variables=None, timeout=30):
        """
        Execute a GraphQL mutation using the NBI (North Bound Interface)
        
        Args:
            mutation (str): The GraphQL mutation string
            variables (dict, optional): Variables for the mutation
            timeout (int, optional): Timeout in seconds (default: 30)
            
        Returns:
            dict: The response data from the GraphQL mutation
            
        Raises:
            RuntimeError: If the mutation fails or times out
        """
        try:
            self.ctx.debug("Executing GraphQL mutation: {}", mutation[:100] + "..." if len(mutation) > 100 else mutation)
            
            if variables:
                self.ctx.debug("Mutation variables: {}", json.dumps(variables, indent=2))
            
            # Prepare the request payload
            payload = {
                "query": mutation
            }
            
            if variables:
                payload["variables"] = variables
            
            # Execute the mutation using emc_nbi
            start_time = time.time()
            response = self.ctx.emc_nbi.mutation(payload, timeout=timeout)
            execution_time = time.time() - start_time
            
            self.ctx.debug("GraphQL mutation executed in {:.2f} seconds", execution_time)
            
            # Check for errors in the response
            if "errors" in response and response["errors"]:
                error_msg = "GraphQL mutation errors: {}".format(json.dumps(response["errors"], indent=2))
                self.ctx.error(error_msg)
                raise RuntimeError(error_msg)
            
            # Log successful response
            if "data" in response:
                self.ctx.debug("GraphQL mutation successful, data keys: {}", list(response["data"].keys()) if response["data"] else "None")
            
            return response
            
        except Exception as e:
            error_msg = "GraphQL mutation failed: {}".format(str(e))
            self.ctx.error(error_msg)
            raise RuntimeError(error_msg)
    
    def nbiRequest(self, query_or_mutation, variables=None, timeout=30, is_mutation=False):
        """
        Generic method to execute either a GraphQL query or mutation
        
        Args:
            query_or_mutation (str): The GraphQL query or mutation string
            variables (dict, optional): Variables for the request
            timeout (int, optional): Timeout in seconds (default: 30)
            is_mutation (bool, optional): Whether this is a mutation (default: False)
            
        Returns:
            dict: The response data from the GraphQL request
        """
        if is_mutation:
            return self.nbiMutation(query_or_mutation, variables, timeout)
        else:
            return self.nbiQuery(query_or_mutation, variables, timeout)