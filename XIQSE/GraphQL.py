import json
import time

class GraphQL(object):
    def __init__(self, context):
        self.ctx = context
    
    def test(self):
        self.ctx.log("XIQSE.GraphQL.test => OK")
    
    def _convert_java_response(self, response):
        """
        Convert Java objects (like HashMap) to Python-compatible format
        
        Args:
            response: The response from NBI API (could be Java object or Python object)
            
        Returns:
            str or dict: Converted response in Python format
        """
        try:
            # Check if it's a Java object
            if hasattr(response, 'toString'):
                # Convert Java object to string
                return str(response)
            elif isinstance(response, dict):
                # Already a Python dict
                return response
            else:
                # Convert to string representation
                return str(response)
        except Exception as e:
            self.ctx.warning("Error converting response: {}", str(e))
            return str(response)
    
    def nbiQuery(self, query, variables=None, timeout=30):
        """
        Execute a GraphQL query using the NBI (North Bound Interface)
        
        Args:
            query (str): The GraphQL query string (with or without 'query' keyword)
            variables (dict, optional): Variables for the query
            timeout (int, optional): Timeout in seconds (default: 30)
            
        Returns:
            dict: The response data from the GraphQL query
            
        Raises:
            RuntimeError: If the query fails or times out
        """
        try:
            # Ensure the query starts with 'query' keyword if not already present
            query_str = query.strip()
            if not query_str.startswith('query') and not query_str.startswith('mutation'):
                query_str = 'query ' + query_str
            
            # Handle variables if provided
            if variables:
                self.ctx.debug("Query variables: {}", json.dumps(variables, indent=2))
                # Note: Variables handling may need to be implemented based on NBI API capabilities
                # For now, we'll log a warning if variables are provided
                self.ctx.warning("Variables provided but may not be supported by NBI API: {}", json.dumps(variables))
            
            self.ctx.debug("Executing GraphQL query: {}", query_str[:100] + "..." if len(query_str) > 100 else query_str)
            
            # Execute the query using emc_nbi (pass query string directly)
            start_time = time.time()
            response = self.ctx.emc_nbi.query(query_str)
            execution_time = time.time() - start_time
            
            self.ctx.debug("GraphQL query executed in {:.2f} seconds", execution_time)
            
            # Convert response to Python-compatible format
            converted_response = self._convert_java_response(response)
            
            # Log the response
            self.ctx.debug("GraphQL query response: {}", converted_response)
            
            # Check for errors if it's a dict
            if isinstance(converted_response, dict) and "errors" in converted_response and converted_response["errors"]:
                error_msg = "GraphQL query errors: {}".format(json.dumps(converted_response["errors"], indent=2))
                self.ctx.error(error_msg)
                raise RuntimeError(error_msg)
            
            # Log successful response if it's a dict
            if isinstance(converted_response, dict) and "data" in converted_response:
                self.ctx.debug("GraphQL query successful, data keys: {}", list(converted_response["data"].keys()) if converted_response["data"] else "None")
            
            return converted_response
            
        except Exception as e:
            error_msg = "GraphQL query failed: {}".format(str(e))
            self.ctx.error(error_msg)
            raise RuntimeError(error_msg)
    
    def nbiMutation(self, mutation, variables=None, timeout=30):
        """
        Execute a GraphQL mutation using the NBI (North Bound Interface)
        
        Args:
            mutation (str): The GraphQL mutation string (with or without 'mutation' keyword)
            variables (dict, optional): Variables for the mutation
            timeout (int, optional): Timeout in seconds (default: 30)
            
        Returns:
            dict: The response data from the GraphQL mutation
            
        Raises:
            RuntimeError: If the mutation fails or times out
        """
        try:
            # Ensure the mutation starts with 'mutation' keyword if not already present
            mutation_str = mutation.strip()
            if not mutation_str.startswith('mutation'):
                mutation_str = 'mutation ' + mutation_str
            
            # Handle variables if provided
            if variables:
                self.ctx.debug("Mutation variables: {}", json.dumps(variables, indent=2))
                # Note: Variables handling may need to be implemented based on NBI API capabilities
                # For now, we'll log a warning if variables are provided
                self.ctx.warning("Variables provided but may not be supported by NBI API: {}", json.dumps(variables))
            
            self.ctx.debug("Executing GraphQL mutation: {}", mutation_str[:100] + "..." if len(mutation_str) > 100 else mutation_str)
            
            # Execute the mutation using emc_nbi (pass mutation string directly)
            start_time = time.time()
            response = self.ctx.emc_nbi.mutation(mutation_str)
            execution_time = time.time() - start_time
            
            self.ctx.debug("GraphQL mutation executed in {:.2f} seconds", execution_time)
            
            # Convert response to Python-compatible format
            converted_response = self._convert_java_response(response)
            
            # Log the response
            self.ctx.debug("GraphQL mutation response: {}", converted_response)
            
            # Check for errors if it's a dict
            if isinstance(converted_response, dict) and "errors" in converted_response and converted_response["errors"]:
                error_msg = "GraphQL mutation errors: {}".format(json.dumps(converted_response["errors"], indent=2))
                self.ctx.error(error_msg)
                raise RuntimeError(error_msg)
            
            # Log successful response if it's a dict
            if isinstance(converted_response, dict) and "data" in converted_response:
                self.ctx.debug("GraphQL mutation successful, data keys: {}", list(converted_response["data"].keys()) if converted_response["data"] else "None")
            
            return converted_response
            
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