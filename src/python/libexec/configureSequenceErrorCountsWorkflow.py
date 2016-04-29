#!/usr/bin/env python
#
# Strelka - Small Variant Caller
# Copyright (c) 2009-2016 Illumina, Inc.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#

"""
This script configures the sequence error counts workflow
"""

import os,sys

scriptDir=os.path.abspath(os.path.dirname(__file__))
scriptName=os.path.basename(__file__)
workflowDir=os.path.abspath(os.path.join(scriptDir,"@THIS_RELATIVE_PYTHON_LIBDIR@"))

sys.path.append(workflowDir)

from configBuildTimeInfo import workflowVersion
from starkaOptions import StarkaWorkflowOptionsBase
from configureUtil import BamSetChecker, groomBamList, joinFile, OptParseException, checkOptionalTabixIndexedFile
from makeRunScript import makeRunScript
from starlingWorkflow import StarlingWorkflow
from workflowUtil import ensureDir, exeFile



class SequenceErrorCountsWorkflowOptions(StarkaWorkflowOptionsBase) :

    def workflowDescription(self) :
        return """Version: %s

This script configures the Strelka sequence error counts workflow.
""" % (workflowVersion)


    def addWorkflowGroupOptions(self,group) :
        group.add_option("--bam", type="string",dest="bamList",metavar="FILE", action="append",
                         help="Sample BAM or CRAM file. [required] (no default)")
        group.add_option("--ploidy", type="string", dest="ploidyBed", metavar="FILE",
                         help="Provide ploidy bed file. The bed records should provide either 1 or 0 in the 5th 'score' column to "
                         "indicate haploid or deleted status respectively. File must be tabix indexed. (no default)")
        group.add_option("--targetRegions", type="string", dest="targetRegionsBed", metavar="FILE",
                         help="Provide bed file of regions to allow variant calls. Calls outside these ares are filtered "
                         "as OffTarget. File must be tabix indexed. (no default)")
        group.add_option("--reportObservedIndels", dest="isReportObservedIndels", action="store_true", default = False,
                         help="Report all observed indels by location in a separate BED file in addition to the"
                         "summary counts")

        StarkaWorkflowOptionsBase.addWorkflowGroupOptions(self,group)


    def getOptionDefaults(self) :

        self.configScriptDir=scriptDir
        defaults=StarkaWorkflowOptionsBase.getOptionDefaults(self)

        libexecDir=defaults["libexecDir"]

        configDir=os.path.abspath(os.path.join(scriptDir,"@THIS_RELATIVE_CONFIGDIR@"))
        assert os.path.isdir(configDir)

        defaults.update({
            'runDir' : 'SequenceErrorCountsWorkflow',
            'getCountsBin' : joinFile(libexecDir,exeFile("GetSequenceErrorCounts")),
            'mergeCountsBin' : joinFile(libexecDir,exeFile("MergeSequenceErrorCounts")),
            'extraCountsArguments' : None
            })
        return defaults



    def validateAndSanitizeExistingOptions(self,options) :

        StarkaWorkflowOptionsBase.validateAndSanitizeExistingOptions(self,options)
        groomBamList(options.bamList,"input")

        def checkFixTabixIndexedFileOption(tabixFile,label):
            checkOptionalTabixIndexedFile(tabixFile,label)
            if tabixFile is None : return None
            return os.path.abspath(tabixFile)

        options.ploidyBed = checkFixTabixIndexedFileOption(options.ploidyBed,"ploidy bed")
        options.targetRegionsBed = checkFixTabixIndexedFileOption(options.targetRegionsBed,"targeted-regions bed")



    def validateOptionExistence(self,options) :

        StarkaWorkflowOptionsBase.validateOptionExistence(self,options)

        bcheck = BamSetChecker()

        def singleAppender(bamList,label):
            if len(bamList) > 1 :
                raise OptParseException("More than one %s sample BAM/CRAM files specified" % (label))
            bcheck.appendBams(bamList,label)

        singleAppender(options.bamList,"Input")
        bcheck.check(options.htsfileBin,
                     options.referenceFasta)



def main() :

    primarySectionName="counts"
    options,iniSections=SequenceErrorCountsWorkflowOptions().getRunOptions(primarySectionName, version=workflowVersion)

    # we don't need to instantiate the workflow object during configuration,
    # but this is done here to trigger additional parameter validation:
    #
    StarlingWorkflow(options,iniSections)

    # generate runscript:
    #
    ensureDir(options.runDir)
    scriptFile=os.path.join(options.runDir,"runWorkflow.py")

    makeRunScript(scriptFile,os.path.join(workflowDir,"sequenceErrorCountsWorkflow.py"),"SequenceErrorCountsWorkflow",primarySectionName,iniSections)

    notefp=sys.stdout
    notefp.write("""
Successfully created workflow run script.
To execute the workflow, run the following script and set appropriate options:

%s
""" % (scriptFile))


if __name__ == "__main__" :
    main()
