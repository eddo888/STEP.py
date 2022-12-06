<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:xs="http://www.w3.org/2001/XMLSchema"
    exclude-result-prefixes="xs"
    version="2.0">
    
    <xsl:output method="xml" indent="yes"/>

    <xsl:template match="DataSet">
        <xsl:copy>
            <xsl:copy-of select="@*"/>
            <xsl:for-each select="DataRow[starts-with(Column[@name='Stereotype']/@value,'STEP')]">
                <xsl:sort select="Column[@name='Stereotype']/@value"></xsl:sort>
                <xsl:copy>
                    <xsl:copy-of select="@*"/>
                    <xsl:apply-templates/>
                </xsl:copy>
            </xsl:for-each>
        </xsl:copy>
    </xsl:template>
   
    <xsl:template match="*">
        <xsl:copy>
            <xsl:copy-of select="@*"/>
            <xsl:apply-templates/>
        </xsl:copy>
    </xsl:template>
    
</xsl:stylesheet>