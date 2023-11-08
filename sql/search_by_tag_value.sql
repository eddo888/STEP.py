select 
       	c.ea_guid as CLASSGUID,
	c.object_type as CLASSTYPE,
	c.name as Name, 
	c.stereotype as Stereotype,
	package.name as PackageName,
	package_p1.name as PackageLevel1,
	package_p2.name as PackageLevel2,
	package_p3.name as PackageLevel3
from (((((t_object c
	inner join t_objectproperties op on op.Object_ID = c.Object_ID)
	inner join t_package as package on c.package_id = package.package_id)
	left join t_package as package_p1 on package_p1.package_id = package.parent_id)
	left join t_package as package_p2 on package_p2.package_id = package_p1.parent_id)
	left join t_package as package_p3 on package_p3.package_id = package_p2.parent_id)
where 
	op.Property = '@ID'
	and 
	op.Value like 'md5js'
	
