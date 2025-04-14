# STEP.py

python libraries to support Stibo STEP MDM APIs

## step.rest.py
```
$ step.rest.py -h
usage: step.rest.py [-h]
                    {step,assets,process-types,processes,instances,objects,products,entities,classifications,endpoints,imports,exports,workflow,tasks,attributes,args}
                    ...

positional arguments:
  {step,assets,process-types,processes,instances,objects,products,entities,classifications,endpoints,imports,exports,workflow,tasks,attributes,args}
                        commands
    step                base class to store the common properties and operations
    assets              MIME type assets
    process-types       background processes running on STEP
    processes           background processes running on STEP
    instances           background processes instances running on STEP
    objects
    products
    entities
    classifications
    endpoints
    imports             MIME type imports
    exports             MIME type exports
    workflow
    tasks
    attributes
    args                print the values for the args

optional arguments:
  -h, --help            show this help message and exit

```

### assets
```
$ step.rest.py assets -h
usage: step.rest.py assets [-h] [-x] [-C CONTEXT] [-F FORMAT] [-H HOSTNAME] [-o OUTPUT]
                           [-P PASSWORD] [-U USERNAME] [-v] [-V VERSION] [-W WORKSPACE] [-X XSLT]
                           {approve,approve_delete,content,create,create_or_replace,delete,get,purge,update}
                           ...

MIME type assets

positional arguments:
  {approve,approve_delete,content,create,create_or_replace,delete,get,purge,update}
                        operations
    approve             approve asset by id
    approve_delete      approve delete asset by id
    content             downlaod the asset to a local directory
    create
    create_or_replace   create or repalce an asset
    delete              delete asset by id
    get                 get the asset by ID
    purge               purge asset by id
    update

optional arguments:
  -h, --help            show this help message and exit
  -x, --asXML           output in xml
  -C CONTEXT, --context CONTEXT
                        default=Context1
  -F FORMAT, --format FORMAT
  -H HOSTNAME, --hostname HOSTNAME
                        default=http://host
  -o OUTPUT, --output OUTPUT
                        output to a file
  -P PASSWORD, --password PASSWORD
  -U USERNAME, --username USERNAME
                        default=stepsys
  -v, --verbose
  -V VERSION, --version VERSION
  -W WORKSPACE, --workspace WORKSPACE
                        default=Main
  -X XSLT, --xslt XSLT

```

### products
```
$ step.rest.py products -h
usage: step.rest.py products [-h] [-x] [-C CONTEXT] [-F FORMAT] [-H HOSTNAME] [-o OUTPUT]
                             [-P PASSWORD] [-U USERNAME] [-v] [-V VERSION] [-W WORKSPACE]
                             [-X XSLT]
                             {approve,approve_delete,children,create,create_or_replace,delete,get,list,purge,reference,references,search,tables,update,values}
                             ...

positional arguments:
  {approve,approve_delete,children,create,create_or_replace,delete,get,list,purge,reference,references,search,tables,update,values}
                        operations
    approve             approve product by id
    approve_delete      approve delete product by id
    children            get children of product by id
    create              create a new product
    create_or_replace   create or repalce a product
    delete              delete product by id
    get                 get product by id
    list                list the products
    purge               purge product by id
    reference           get references of product by id
    references          get references of product by id
    search              search for a product
    tables              get tables of product by id
    update              set values of product by id
    values              get values of product by id

optional arguments:
  -h, --help            show this help message and exit
  -x, --asXML           output in xml
  -C CONTEXT, --context CONTEXT
                        default=Context1
  -F FORMAT, --format FORMAT
  -H HOSTNAME, --hostname HOSTNAME
                        default=http://host
  -o OUTPUT, --output OUTPUT
                        output to a file
  -P PASSWORD, --password PASSWORD
  -U USERNAME, --username USERNAME
                        default=stepsys
  -v, --verbose
  -V VERSION, --version VERSION
  -W WORKSPACE, --workspace WORKSPACE
                        default=Main
  -X XSLT, --xslt XSLT

```

### classifications
```
$ step.rest.py classifications -h
usage: step.rest.py classifications [-h] [-x] [-C CONTEXT] [-F FORMAT] [-H HOSTNAME] [-o OUTPUT]
                                    [-P PASSWORD] [-r ROOT] [-U USERNAME] [-v] [-V VERSION]
                                    [-W WORKSPACE] [-X XSLT]
                                    {approve,approve_delete,assets,children,create,create_or_replace,delete,get,list,purge,references,update,values}
                                    ...

positional arguments:
  {approve,approve_delete,assets,children,create,create_or_replace,delete,get,list,purge,references,update,values}
                        operations
    approve             approve classification by id
    approve_delete      approve delete classification by id
    assets              get children of classification by id
    children            get children of classification by id
    create              create a new classification
    create_or_replace   create or repalce a classification
    delete              delete classification by id
    get                 get classification by id
    list                list of children of classification hierarchy root
    purge               purge classification by id
    references          get children of classification by id
    update              set values of classification by id
    values              get values of classification by id

optional arguments:
  -h, --help            show this help message and exit
  -x, --asXML           output in xml
  -C CONTEXT, --context CONTEXT
                        default=Context1
  -F FORMAT, --format FORMAT
  -H HOSTNAME, --hostname HOSTNAME
                        default=http://host
  -o OUTPUT, --output OUTPUT
                        output to a file
  -P PASSWORD, --password PASSWORD
  -r ROOT, --root ROOT  default=Metcash_Root_Metcash
  -U USERNAME, --username USERNAME
                        default=stepsys
  -v, --verbose
  -V VERSION, --version VERSION
  -W WORKSPACE, --workspace WORKSPACE
                        default=Main
  -X XSLT, --xslt XSLT

```

### entities
```
$ step.rest.py entities -h
usage: step.rest.py entities [-h] [-x] [-C CONTEXT] [-F FORMAT] [-H HOSTNAME] [-o OUTPUT]
                             [-P PASSWORD] [-r ROOT] [-U USERNAME] [-v] [-V VERSION]
                             [-W WORKSPACE] [-X XSLT]
                             {approve,approve_delete,children,create,create_or_replace,delete,get,list,purge,search,update,values}
                             ...

positional arguments:
  {approve,approve_delete,children,create,create_or_replace,delete,get,list,purge,search,update,values}
                        operations
    approve             approve entity by id
    approve_delete      approve delete entity by id
    children            get children of entity by id
    create              create a new entity
    create_or_replace   create or repalce an entity
    delete              delete entity by id
    get                 get entity by id
    list                list of children of entity hierarchy root
    purge               purge entity by id
    search              search for entities
    update              update values of entity by id
    values              get values of entity by id

optional arguments:
  -h, --help            show this help message and exit
  -x, --asXML           output in xml
  -C CONTEXT, --context CONTEXT
                        default=Context1
  -F FORMAT, --format FORMAT
  -H HOSTNAME, --hostname HOSTNAME
                        default=http://host
  -o OUTPUT, --output OUTPUT
                        output to a file
  -P PASSWORD, --password PASSWORD
  -r ROOT, --root ROOT  default=Entity hierarchy root
  -U USERNAME, --username USERNAME
                        default=stepsys
  -v, --verbose
  -V VERSION, --version VERSION
  -W WORKSPACE, --workspace WORKSPACE
                        default=Main
  -X XSLT, --xslt XSLT

```

---
## step.soap.py
```
usage: step.soap.py [-h] [-H HOSTNAME] [-p PASSWORD] [-u USERNAME] [-v] [-w WSDLPATH] [-o OUTPUT]
                    [-c]
                    {addClassification,approve,createClassification,createProduct,createReference,deleteNode,describe,directory,dummy,getAttributeDetails,getBackgoundProcesses,getBaseProduct,getChildren,getClassifications,getContexts,getGroups,getLOVValueIDs,getName,getNodeDetails,getPath,getReferenceTypes,getReferences,getTasks,getUserInfo,getUsers,getValidChildTypes,getValues,getWorkflowProcessDetail,getWorkflowProcesses,getWorkspaces,moveNode,queryByAttribute,queryById,service,setName,setValues,startWorkflow,types,args}
                    ...

positional arguments:
  {addClassification,approve,createClassification,createProduct,createReference,deleteNode,describe,directory,dummy,getAttributeDetails,getBackgoundProcesses,getBaseProduct,getChildren,getClassifications,getContexts,getGroups,getLOVValueIDs,getName,getNodeDetails,getPath,getReferenceTypes,getReferences,getTasks,getUserInfo,getUsers,getValidChildTypes,getValues,getWorkflowProcessDetail,getWorkflowProcesses,getWorkspaces,moveNode,queryByAttribute,queryById,service,setName,setValues,startWorkflow,types,args}
                        operations
    addClassification
    approve
    createClassification
    createProduct
    createReference
    deleteNode
    describe            describe a method
    directory           print out the client specification
    dummy               describe a method
    getAttributeDetails
    getBackgoundProcesses
    getBaseProduct
    getChildren
    getClassifications
    getContexts
    getGroups
    getLOVValueIDs
    getName
    getNodeDetails
    getPath
    getReferenceTypes
    getReferences
    getTasks
    getUserInfo
    getUsers
    getValidChildTypes
    getValues
    getWorkflowProcessDetail
    getWorkflowProcesses
    getWorkspaces
    moveNode
    queryByAttribute
    queryById
    service
    setName
    setValues
    startWorkflow
    types               print out the client types
    args                print the values for the args

optional arguments:
  -h, --help            show this help message and exit
  -H HOSTNAME, --hostname HOSTNAME
                        default=http://host
  -p PASSWORD, --password PASSWORD
  -u USERNAME, --username USERNAME
                        default=stepsys
  -v, --verbose
  -w WSDLPATH, --wsdlpath WSDLPATH
                        default=StepWS/stepws?wsdl
  -o OUTPUT, --output OUTPUT
                        output to file
  -c, --colour          in colour
  ```
  
# jscript libraries for Sparx

the following helper libraries are in Sparx jScript
create a "User Scripts" folder,
then create a new jscript .js file for each of the following

["Library.js" base shared library](https://github.com/eddo888/STEP.py/raw/master/jscript/Library.js)

["IncludeMissingParts.js" will look for missing items in this package and add to the diagram if not there](https://github.com/eddo888/STEP.py/raw/master/jscript/IncludeMissingParts.js) 

["IncludeLInkedParts.js" to find referenced parts on selected items and add to the current diagram](https://github.com/eddo888/STEP.py/raw/master/jscript/IncludeLinkedParts.js)

["set-stereotype.js" set the STEP stereotype for selected diagram items](https://github.com/eddo888/STEP.py/raw/master/jscript/set_stereotype.js)

# uml resources for Sparx

this Sparx Resource file can be used to create colour profiles for UML types.

["UML-Reference-Stereotypes.sparxea.xml" Sparx->Configure->Model->Transfer->Import Reference Data, then select file and choose specifications](https://github.com/eddo888/STEP.py/raw/master/UML/UML-Reference-Stereotypes.sparxea.xml)






