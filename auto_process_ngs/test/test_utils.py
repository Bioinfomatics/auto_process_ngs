#######################################################################
# Tests for utils.py module
#######################################################################

import unittest
import tempfile
import shutil
import zipfile
from bcftbx.JobRunner import SimpleJobRunner,GEJobRunner
from bcftbx.utils import find_program
from auto_process_ngs.mock import MockAnalysisDirFactory
from auto_process_ngs.mock import MockAnalysisProject
from auto_process_ngs.applications import Command
from auto_process_ngs.utils import *

class TestAnalysisFastq(unittest.TestCase):
    """Tests for the AnalysisFastq class

    """

    def test_full_name(self):
        """Handle full Illumina-style fastq name
        """
        fq = AnalysisFastq('NH1_ChIP-seq_Gli1_ACAGTG_L003_R2_001')
        self.assertEqual(fq.sample_name,'NH1_ChIP-seq_Gli1')
        self.assertEqual(fq.basename,
                         'NH1_ChIP-seq_Gli1_ACAGTG_L003_R2_001')
        self.assertEqual(fq.extension,'')
        self.assertEqual(fq.sample_number,None)
        self.assertEqual(fq.barcode_sequence,'ACAGTG')
        self.assertEqual(fq.lane_number,3)
        self.assertEqual(fq.read_number,2)
        self.assertEqual(fq.set_number,1)
        self.assertFalse(fq.is_index_read)
        self.assertEqual(str(fq),'NH1_ChIP-seq_Gli1_ACAGTG_L003_R2_001')

    def test_full_name_dual_index(self):
        """Handle full Illumina-style fastq name with dual index
        """
        fq = AnalysisFastq('NH1_ChIP-seq_Gli1_ACAGTG-GTTCAC_L003_R2_001')
        self.assertEqual(fq.sample_name,'NH1_ChIP-seq_Gli1')
        self.assertEqual(fq.basename,
                         'NH1_ChIP-seq_Gli1_ACAGTG-GTTCAC_L003_R2_001')
        self.assertEqual(fq.extension,'')
        self.assertEqual(fq.sample_number,None)
        self.assertEqual(fq.barcode_sequence,'ACAGTG-GTTCAC')
        self.assertEqual(fq.lane_number,3)
        self.assertEqual(fq.read_number,2)
        self.assertEqual(fq.set_number,1)
        self.assertFalse(fq.is_index_read)
        self.assertEqual(str(fq),'NH1_ChIP-seq_Gli1_ACAGTG-GTTCAC_L003_R2_001')

    def test_full_name_blc2fastq2(self):
        """Handle Illumina fastq name from bcl2fastq2
        """
        fq = AnalysisFastq('NH1_ChIP-seq_Gli1_S4_L003_R2_001')
        self.assertEqual(fq.sample_name,'NH1_ChIP-seq_Gli1')
        self.assertEqual(fq.basename,
                         'NH1_ChIP-seq_Gli1_S4_L003_R2_001')
        self.assertEqual(fq.extension,'')
        self.assertEqual(fq.sample_number,4)
        self.assertEqual(fq.barcode_sequence,None)
        self.assertEqual(fq.lane_number,3)
        self.assertEqual(fq.read_number,2)
        self.assertEqual(fq.set_number,1)
        self.assertFalse(fq.is_index_read)
        self.assertEqual(str(fq),'NH1_ChIP-seq_Gli1_S4_L003_R2_001')

    def test_index_read_blc2fastq2(self):
        """Handle Illumina index read fastq name from bcl2fastq2
        """
        fq = AnalysisFastq('NH1_ChIP-seq_Gli1_S4_L003_I1_001')
        self.assertEqual(fq.sample_name,'NH1_ChIP-seq_Gli1')
        self.assertEqual(fq.sample_number,4)
        self.assertEqual(fq.barcode_sequence,None)
        self.assertEqual(fq.lane_number,3)
        self.assertEqual(fq.read_number,1)
        self.assertEqual(fq.set_number,1)
        self.assertTrue(fq.is_index_read)
        self.assertEqual(str(fq),'NH1_ChIP-seq_Gli1_S4_L003_I1_001')

    def test_name_no_lane_blc2fastq2(self):
        """Handle Illumina fastq name from bcl2fastq2 (without lane)
        """
        fq = AnalysisFastq('NH1_ChIP-seq_Gli1_S4_R2_001')
        self.assertEqual(fq.sample_name,'NH1_ChIP-seq_Gli1')
        self.assertEqual(fq.basename,
                         'NH1_ChIP-seq_Gli1_S4_R2_001')
        self.assertEqual(fq.extension,'')
        self.assertEqual(fq.sample_number,4)
        self.assertEqual(fq.barcode_sequence,None)
        self.assertEqual(fq.lane_number,None)
        self.assertEqual(fq.read_number,2)
        self.assertEqual(fq.set_number,1)
        self.assertFalse(fq.is_index_read)
        self.assertEqual(str(fq),'NH1_ChIP-seq_Gli1_S4_R2_001')

    def test_name_only(self):
        """Handle reduced fastq name (sample name only)
        """
        fq = AnalysisFastq('NH1_ChIP-seq_Gli1')
        self.assertEqual(fq.sample_name,'NH1_ChIP-seq_Gli1')
        self.assertEqual(fq.basename,'NH1_ChIP-seq_Gli1')
        self.assertEqual(fq.extension,'')
        self.assertEqual(fq.sample_number,None)
        self.assertEqual(fq.barcode_sequence,None)
        self.assertEqual(fq.lane_number,None)
        self.assertEqual(fq.read_number,None)
        self.assertEqual(fq.set_number,None)
        self.assertFalse(fq.is_index_read)
        self.assertEqual(str(fq),'NH1_ChIP-seq_Gli1')

    def test_name_only_paired_end(self):
        """Handle reduced fastq name (sample name only, paired end)
        """
        fq = AnalysisFastq('NH1_ChIP-seq_Gli1_R2')
        self.assertEqual(fq.sample_name,'NH1_ChIP-seq_Gli1')
        self.assertEqual(fq.basename,'NH1_ChIP-seq_Gli1_R2')
        self.assertEqual(fq.extension,'')
        self.assertEqual(fq.sample_number,None)
        self.assertEqual(fq.barcode_sequence,None)
        self.assertEqual(fq.lane_number,None)
        self.assertEqual(fq.read_number,2)
        self.assertEqual(fq.set_number,None)
        self.assertFalse(fq.is_index_read)
        self.assertEqual(str(fq),'NH1_ChIP-seq_Gli1_R2')

    def test_name_and_lane(self):
        """Handle reduced fastq name (sample name and lane)
        """
        fq = AnalysisFastq('NH1_ChIP-seq_Gli1_L001')
        self.assertEqual(fq.sample_name,'NH1_ChIP-seq_Gli1')
        self.assertEqual(fq.basename,'NH1_ChIP-seq_Gli1_L001')
        self.assertEqual(fq.extension,'')
        self.assertEqual(fq.sample_number,None)
        self.assertEqual(fq.barcode_sequence,None)
        self.assertEqual(fq.lane_number,1)
        self.assertEqual(fq.read_number,None)
        self.assertEqual(fq.set_number,None)
        self.assertFalse(fq.is_index_read)
        self.assertEqual(str(fq),'NH1_ChIP-seq_Gli1_L001')

    def test_name_and_lane_paired_end(self):
        """Handle reduced fastq name (sample name and lane, paired end)
        """
        fq = AnalysisFastq('NH1_ChIP-seq_Gli1_L001_R2')
        self.assertEqual(fq.sample_name,'NH1_ChIP-seq_Gli1')
        self.assertEqual(fq.basename,'NH1_ChIP-seq_Gli1_L001_R2')
        self.assertEqual(fq.extension,'')
        self.assertEqual(fq.sample_number,None)
        self.assertEqual(fq.barcode_sequence,None)
        self.assertEqual(fq.lane_number,1)
        self.assertEqual(fq.read_number,2)
        self.assertEqual(fq.set_number,None)
        self.assertFalse(fq.is_index_read)
        self.assertEqual(str(fq),'NH1_ChIP-seq_Gli1_L001_R2')

    def test_name_and_tag(self):
        """Handle reduced fastq name (sample name and barcode)
        """
        fq = AnalysisFastq('NH1_ChIP-seq_Gli1_ACAGTG')
        self.assertEqual(fq.sample_name,'NH1_ChIP-seq_Gli1')
        self.assertEqual(fq.basename,'NH1_ChIP-seq_Gli1_ACAGTG')
        self.assertEqual(fq.extension,'')
        self.assertEqual(fq.sample_number,None)
        self.assertEqual(fq.barcode_sequence,'ACAGTG')
        self.assertEqual(fq.lane_number,None)
        self.assertEqual(fq.read_number,None)
        self.assertEqual(fq.set_number,None)
        self.assertFalse(fq.is_index_read)
        self.assertEqual(str(fq),'NH1_ChIP-seq_Gli1_ACAGTG')

    def test_name_and_tag_paired_end(self):
        """Handle reduced fastq name (sample name and barcode, paired end)
        """
        fq = AnalysisFastq('NH1_ChIP-seq_Gli1_ACAGTG_R2')
        self.assertEqual(fq.sample_name,'NH1_ChIP-seq_Gli1')
        self.assertEqual(fq.basename,'NH1_ChIP-seq_Gli1_ACAGTG_R2')
        self.assertEqual(fq.extension,'')
        self.assertEqual(fq.sample_number,None)
        self.assertEqual(fq.barcode_sequence,'ACAGTG')
        self.assertEqual(fq.lane_number,None)
        self.assertEqual(fq.read_number,2)
        self.assertEqual(fq.set_number,None)
        self.assertFalse(fq.is_index_read)
        self.assertEqual(str(fq),'NH1_ChIP-seq_Gli1_ACAGTG_R2')

    def test_name_tag_and_lane(self):
        """Handle reduced fastq name (sample name, barcode and lane)
        """
        fq = AnalysisFastq('NH1_ChIP-seq_Gli1_ACAGTG_L001')
        self.assertEqual(fq.sample_name,'NH1_ChIP-seq_Gli1')
        self.assertEqual(fq.basename,'NH1_ChIP-seq_Gli1_ACAGTG_L001')
        self.assertEqual(fq.extension,'')
        self.assertEqual(fq.sample_number,None)
        self.assertEqual(fq.barcode_sequence,'ACAGTG')
        self.assertEqual(fq.lane_number,1)
        self.assertEqual(fq.read_number,None)
        self.assertEqual(fq.set_number,None)
        self.assertFalse(fq.is_index_read)
        self.assertEqual(str(fq),'NH1_ChIP-seq_Gli1_ACAGTG_L001')

    def test_name_tag_and_lane_paired_end(self):
        """Handle reduced fastq name (sample name, barcode and lane, paired end)
        """
        fq = AnalysisFastq('NH1_ChIP-seq_Gli1_ACAGTG_L001_R2')
        self.assertEqual(fq.sample_name,'NH1_ChIP-seq_Gli1')
        self.assertEqual(fq.basename,'NH1_ChIP-seq_Gli1_ACAGTG_L001_R2')
        self.assertEqual(fq.extension,'')
        self.assertEqual(fq.sample_number,None)
        self.assertEqual(fq.barcode_sequence,'ACAGTG')
        self.assertEqual(fq.lane_number,1)
        self.assertEqual(fq.read_number,2)
        self.assertEqual(fq.set_number,None)
        self.assertFalse(fq.is_index_read)
        self.assertEqual(str(fq),'NH1_ChIP-seq_Gli1_ACAGTG_L001_R2')

    def test_AGTC_sample_names(self):
        """Handle sample names consisting of letters 'A', 'G', 'T' and 'C'
        """
        for name in ('A','G','T','C','AGCT'):
            fq = AnalysisFastq('%s_R1' % name)
            self.assertEqual(fq.sample_name,name)
            self.assertEqual(fq.sample_number,None)
            self.assertEqual(fq.barcode_sequence,None)
            self.assertEqual(fq.lane_number,None)
            self.assertEqual(fq.read_number,1)
            self.assertEqual(fq.set_number,None)
            self.assertFalse(fq.is_index_read)
            self.assertEqual(str(fq),'%s_R1' % name)

    def test_non_standard_sample_name(self):
        """Handle non-standard Fastq names with sample name only
        """
        fq = AnalysisFastq('NH1_ChIP-seq.r2')
        self.assertEqual(fq.sample_name,'NH1_ChIP-seq')
        self.assertEqual(fq.basename,'NH1_ChIP-seq.r2')
        self.assertEqual(fq.extension,'')
        self.assertEqual(fq.sample_number,None)
        self.assertEqual(fq.barcode_sequence,None)
        self.assertEqual(fq.lane_number,None)
        self.assertEqual(fq.read_number,2)
        self.assertEqual(fq.set_number,None)
        self.assertFalse(fq.is_index_read)
        self.assertEqual(str(fq),'NH1_ChIP-seq.r2')

    def test_non_standard_sample_name_with_dots(self):
        """Handle non-standard Fastq names with sample name containing dots
        """
        fq = AnalysisFastq('NH1.2.r2')
        self.assertEqual(fq.sample_name,'NH1.2')
        self.assertEqual(fq.basename,'NH1.2.r2')
        self.assertEqual(fq.extension,'')
        self.assertEqual(fq.sample_number,None)
        self.assertEqual(fq.barcode_sequence,None)
        self.assertEqual(fq.lane_number,None)
        self.assertEqual(fq.read_number,2)
        self.assertEqual(fq.set_number,None)
        self.assertEqual(str(fq),'NH1.2.r2')

    def test_non_standard_sample_name_and_barcode(self):
        """Handle non-standard Fastq names with sample name and barcode
        """
        fq = AnalysisFastq('NH1_ChIP-seq.ACAGTG.r2')
        self.assertEqual(fq.sample_name,'NH1_ChIP-seq')
        self.assertEqual(fq.basename,'NH1_ChIP-seq.ACAGTG.r2')
        self.assertEqual(fq.extension,'')
        self.assertEqual(fq.sample_number,None)
        self.assertEqual(fq.barcode_sequence,'ACAGTG')
        self.assertEqual(fq.lane_number,None)
        self.assertEqual(fq.read_number,2)
        self.assertEqual(fq.set_number,None)
        self.assertFalse(fq.is_index_read)
        self.assertEqual(str(fq),'NH1_ChIP-seq.ACAGTG.r2')

    def test_input_is_full_path(self):
        """Handle input as full path to Fastq file
        """
        fq = AnalysisFastq('/data/Project_NH/Sample_NH1/NH1_ChIP-seq_Gli1_ACAGTG_L003_R2_001.fastq.gz')
        self.assertEqual(fq.sample_name,'NH1_ChIP-seq_Gli1')
        self.assertEqual(fq.basename,'NH1_ChIP-seq_Gli1_ACAGTG_L003_R2_001')
        self.assertEqual(fq.extension,'.fastq.gz')
        self.assertEqual(fq.sample_number,None)
        self.assertEqual(fq.barcode_sequence,'ACAGTG')
        self.assertEqual(fq.lane_number,3)
        self.assertEqual(fq.read_number,2)
        self.assertEqual(fq.set_number,1)
        self.assertFalse(fq.is_index_read)
        self.assertEqual(str(fq),'NH1_ChIP-seq_Gli1_ACAGTG_L003_R2_001')

class TestAnalysisDir(unittest.TestCase):
    """Tests for the AnalysisDir class

    """
    def setUp(self):
        self.dirn = tempfile.mkdtemp(suffix='TestAnalysisDir')

    def tearDown(self):
        # Remove the temporary test directory
        shutil.rmtree(self.dirn)

    def test_casava(self):
        """Check AnalysisDir against CASAVA-style output
        """
        mockdir = MockAnalysisDirFactory.casava(
            '160621_M00879_0087_000000000-AGEW9',
            'miseq',
            top_dir=self.dirn)
        mockdir.create()
        analysis_dir = AnalysisDir(mockdir.dirn)
        self.assertEqual(analysis_dir.run_name,mockdir.run_name)
        self.assertEqual(analysis_dir.n_sequencing_data,1)
        self.assertEqual(analysis_dir.n_projects,2)
        self.assertTrue(analysis_dir.paired_end)

    def test_bcl2fastq2(self):
        """Check AnalysisDir against bcl2fastq v2-style output
        """
        mockdir = MockAnalysisDirFactory.bcl2fastq2(
            '160621_M00879_0087_000000000-AGEW9',
            'miseq',
            top_dir=self.dirn)
        mockdir.create()
        analysis_dir = AnalysisDir(mockdir.dirn)
        self.assertEqual(analysis_dir.run_name,mockdir.run_name)
        self.assertEqual(analysis_dir.n_sequencing_data,1)
        self.assertEqual(analysis_dir.n_projects,2)
        self.assertTrue(analysis_dir.paired_end)

    def test_handle_non_project_dir(self):
        """Check AnalysisDir with non-project directory
        """
        mockdir = MockAnalysisDirFactory.bcl2fastq2(
            '160621_M00879_0087_000000000-AGEW9',
            'miseq',
            top_dir=self.dirn)
        mockdir.create()
        # Add non-project dir
        non_project_dir = os.path.join(self.dirn,
                                '160621_M00879_0087_000000000-AGEW9_analysis',
                                'extras')
        fqs_dir = os.path.join(non_project_dir,'fastqs')
        os.mkdir(non_project_dir)
        os.mkdir(fqs_dir)
        for fq in ('PB04_S4_R1_unpaired.fastq.gz',
                   'PB04_trimmoPE_bowtie2_notHg38.1.fastq.gz'):
            with open(os.path.join(fqs_dir,fq),'w') as fp:
                fp.write("")
        # Load and check the analysis dir
        analysis_dir = AnalysisDir(mockdir.dirn)
        self.assertEqual(analysis_dir.run_name,mockdir.run_name)
        self.assertEqual(analysis_dir.n_sequencing_data,1)
        self.assertEqual(analysis_dir.n_projects,2)
        self.assertTrue(analysis_dir.paired_end)

class TestAnalysisProject(unittest.TestCase):
    """Tests for the AnalysisProject class

    """
    def setUp(self):
        # Create a temporary directory for tests
        self.dirn = tempfile.mkdtemp(suffix='TestAnalysisProject')

    def make_data_dir(self,fastq_list):
        # Make a fake data source directory
        self.fastqs = []
        fake_fastqs_dir = os.path.join(self.dirn,'fake_fastqs')
        os.mkdir(fake_fastqs_dir)
        for fq in fastq_list:
            fastq = os.path.join(fake_fastqs_dir,fq)
            open(fastq,'w').close()
            self.fastqs.append(fastq)

    def make_mock_project_dir(self,name,fastq_list,fastq_dir='fastqs',
                              primary_fastq_dir=None):
        # Make a mock project directory
        if primary_fastq_dir is None:
            primary_fastq_dir = fastq_dir
        sample_names = list(
            set([AnalysisFastq(fq).sample_name for fq in fastq_list]))
        sample_names.sort()
        n_samples = len(sample_names)
        sample_names = "%d sample%s (%s)" % \
                       (n_samples,
                        '' if n_samples == 1 else 's',
                        ', '.join(sample_names))
        metadata = { 'Primary fastqs': primary_fastq_dir,
                     'Samples': sample_names }
        MockAnalysisProject(name,
                            fastq_list,
                            fastq_dir=fastq_dir,
                            metadata=metadata).create(top_dir=self.dirn)

    def tearDown(self):
        # Remove the temporary test directory
        shutil.rmtree(self.dirn)

    def test_empty_analysis_project(self):
        """Check empty AnalysisProject class
        """
        dirn = os.path.join(self.dirn,'PJB')
        project = AnalysisProject('PJB',dirn)
        self.assertEqual(project.name,'PJB')
        self.assertEqual(project.dirn,dirn)
        self.assertEqual(project.samples,[])
        self.assertFalse(project.multiple_fastqs)
        self.assertEqual(project.fastq_dir,None)
        self.assertEqual(project.info.library_type,None)
        self.assertEqual(project.info.single_cell_platform,None)
        self.assertEqual(project.info.organism,None)
        self.assertEqual(project.info.number_of_cells,None)
        self.assertEqual(project.info.icell8_well_list,None)
        self.assertFalse(project.info.paired_end)
        self.assertEqual(project.info.platform,None)
        self.assertEqual(project.info.primary_fastq_dir,None)
        self.assertEqual(project.info.samples,None)
        self.assertEqual(project.fastq_dirs,[])

    def test_create_single_end_analysis_project(self):
        """Check creation of new single-end AnalysisProject directory
        """
        self.make_data_dir(('PJB1-A_ACAGTG_L001_R1_001.fastq.gz',
                            'PJB1-B_ACAGTG_L002_R1_001.fastq.gz',))
        dirn = os.path.join(self.dirn,'PJB')
        project = AnalysisProject('PJB',dirn)
        project.create_directory(fastqs=self.fastqs)
        self.assertEqual(project.name,'PJB')
        self.assertTrue(os.path.isdir(project.dirn))
        self.assertFalse(project.multiple_fastqs)
        self.assertFalse(project.info.paired_end)
        self.assertEqual(project.info.primary_fastq_dir,'fastqs')
        self.assertEqual(project.info.samples,'2 samples (PJB1-A, PJB1-B)')
        self.assertEqual(project.samples[0].name,'PJB1-A')
        self.assertEqual(project.samples[1].name,'PJB1-B')
        self.assertEqual(project.fastq_dir,
                         os.path.join(project.dirn,'fastqs'))
        self.assertEqual(project.fastq_dirs,['fastqs',])

    def test_create_single_end_analysis_project_multi_fastqs(self):
        """Check creation of new single-end AnalysisProject directory (multi-fastq/sample)
        """
        self.make_data_dir(('PJB1-A_ACAGTG_L001_R1_001.fastq.gz',
                            'PJB1-A_ACAGTG_L002_R1_001.fastq.gz',
                            'PJB1-B_ACAGTG_L001_R1_001.fastq.gz',
                            'PJB1-B_ACAGTG_L002_R1_001.fastq.gz',))
        dirn = os.path.join(self.dirn,'PJB')
        project = AnalysisProject('PJB',dirn)
        project.create_directory(fastqs=self.fastqs)
        self.assertEqual(project.name,'PJB')
        self.assertTrue(os.path.isdir(project.dirn))
        self.assertTrue(project.multiple_fastqs)
        self.assertFalse(project.info.paired_end)
        self.assertEqual(project.info.primary_fastq_dir,'fastqs')
        self.assertEqual(project.info.samples,
                         '2 samples (PJB1-A, PJB1-B, multiple fastqs per sample)')
        self.assertEqual(project.samples[0].name,'PJB1-A')
        self.assertEqual(project.samples[1].name,'PJB1-B')
        self.assertEqual(project.fastq_dir,
                         os.path.join(project.dirn,'fastqs'))
        self.assertEqual(project.fastq_dirs,['fastqs',])

    def test_create_paired_end_analysis_project(self):
        """Check creation of new paired-end AnalysisProject directory
        """
        self.make_data_dir(('PJB1-A_ACAGTG_L001_R1_001.fastq.gz',
                            'PJB1-B_ACAGTG_L002_R1_001.fastq.gz',
                            'PJB1-A_ACAGTG_L001_R2_001.fastq.gz',
                            'PJB1-B_ACAGTG_L002_R2_001.fastq.gz',))
        dirn = os.path.join(self.dirn,'PJB')
        project = AnalysisProject('PJB',dirn,fastq_dir='fastqs.test')
        project.create_directory(fastqs=self.fastqs)
        self.assertEqual(project.name,'PJB')
        self.assertTrue(os.path.isdir(project.dirn))
        self.assertFalse(project.multiple_fastqs)
        self.assertTrue(project.info.paired_end)
        self.assertEqual(project.info.primary_fastq_dir,'fastqs')
        self.assertEqual(project.info.samples,'2 samples (PJB1-A, PJB1-B)')
        self.assertEqual(project.samples[0].name,'PJB1-A')
        self.assertEqual(project.samples[1].name,'PJB1-B')
        self.assertEqual(project.fastq_dir,
                         os.path.join(project.dirn,'fastqs'))
        self.assertEqual(project.fastq_dirs,['fastqs',])

    def test_create_paired_end_analysis_project_multi_fastqs(self):
        """Check creation of new paired-end AnalysisProject directory (multi-fastq/sample)
        """
        self.make_data_dir(('PJB1-B_ACAGTG_L001_R1_001.fastq.gz',
                            'PJB1-B_ACAGTG_L002_R1_001.fastq.gz',
                            'PJB1-B_ACAGTG_L001_R2_001.fastq.gz',
                            'PJB1-B_ACAGTG_L002_R2_001.fastq.gz',))
        dirn = os.path.join(self.dirn,'PJB')
        project = AnalysisProject('PJB',dirn)
        project.create_directory(fastqs=self.fastqs)
        self.assertEqual(project.name,'PJB')
        self.assertTrue(os.path.isdir(project.dirn))
        self.assertEqual(project.samples[0].name,'PJB1-B')
        self.assertTrue(project.multiple_fastqs)
        self.assertTrue(project.info.paired_end)
        self.assertEqual(project.fastq_dir,
                         os.path.join(project.dirn,'fastqs'))
        self.assertEqual(project.fastq_dirs,['fastqs',])
        self.assertEqual(project.info.primary_fastq_dir,'fastqs')
        self.assertEqual(project.info.samples,
                         '1 sample (PJB1-B, multiple fastqs per sample)')

    def test_create_analysis_project_not_standard_fastq_dir(self):
        """Check creation of AnalysisProject directory with non-standard fastq dir
        """
        self.make_data_dir(('PJB1-B_ACAGTG_L001_R1_001.fastq.gz',
                            'PJB1-B_ACAGTG_L002_R1_001.fastq.gz',
                            'PJB1-B_ACAGTG_L001_R2_001.fastq.gz',
                            'PJB1-B_ACAGTG_L002_R2_001.fastq.gz',))
        dirn = os.path.join(self.dirn,'PJB')
        project = AnalysisProject('PJB',dirn)
        project.create_directory(fastqs=self.fastqs,fastq_dir='fastqs.test')
        self.assertEqual(project.name,'PJB')
        self.assertTrue(os.path.isdir(project.dirn))
        self.assertEqual(project.samples[0].name,'PJB1-B')
        self.assertTrue(project.multiple_fastqs)
        self.assertTrue(project.info.paired_end)
        self.assertEqual(project.fastq_dir,
                         os.path.join(project.dirn,'fastqs.test'))
        self.assertEqual(project.info.samples,
                         '1 sample (PJB1-B, multiple fastqs per sample)')
        self.assertEqual(project.fastq_dirs,['fastqs.test',])
        self.assertEqual(project.info.primary_fastq_dir,'fastqs.test')

    def test_load_single_end_analysis_project(self):
        """Check loading of an existing single-end AnalysisProject directory
        """
        self.make_mock_project_dir(
            'PJB',
            ('PJB1-A_ACAGTG_L001_R1_001.fastq.gz',
             'PJB1-B_ACAGTG_L002_R1_001.fastq.gz',))
        dirn = os.path.join(self.dirn,'PJB')
        project = AnalysisProject('PJB',dirn)
        self.assertEqual(project.name,'PJB')
        self.assertTrue(os.path.isdir(project.dirn))
        self.assertFalse(project.multiple_fastqs)
        self.assertFalse(project.info.paired_end)
        self.assertEqual(project.samples[0].name,'PJB1-A')
        self.assertEqual(project.samples[1].name,'PJB1-B')
        self.assertEqual(project.fastq_dir,
                         os.path.join(project.dirn,'fastqs'))
        self.assertEqual(project.info.samples,'2 samples (PJB1-A, PJB1-B)')
        self.assertEqual(project.fastq_dirs,['fastqs',])
        self.assertEqual(project.info.primary_fastq_dir,'fastqs')

    def test_load_analysis_project_non_canonical_fastq_dir(self):
        """Check AnalysisProject loading for directory with non-canonical fastq directory
        """
        self.make_mock_project_dir(
            'PJB',
            ('PJB1-A_ACAGTG_L001_R1_001.fastq.gz',
             'PJB1-B_ACAGTG_L002_R1_001.fastq.gz',),
            fastq_dir='fastqs.test')
        dirn = os.path.join(self.dirn,'PJB')
        project = AnalysisProject('PJB',dirn,fastq_dir='fastqs.test')
        self.assertEqual(project.name,'PJB')
        self.assertTrue(os.path.isdir(project.dirn))
        self.assertFalse(project.multiple_fastqs)
        self.assertFalse(project.info.paired_end)
        self.assertEqual(project.samples[0].name,'PJB1-A')
        self.assertEqual(project.samples[1].name,'PJB1-B')
        self.assertEqual(project.fastq_dir,
                         os.path.join(project.dirn,'fastqs.test'))
        self.assertEqual(project.info.samples,'2 samples (PJB1-A, PJB1-B)')
        self.assertEqual(project.fastq_dirs,['fastqs.test',])
        self.assertEqual(project.info.primary_fastq_dir,'fastqs.test')

    def test_load_analysis_project_non_canonical_fastqs(self):
        """Check AnalysisProject loading fails for directory with non-canonical fastqs
        """
        self.make_mock_project_dir(
            'PJB',
            ('PB04_S4_R1_unpaired.fastq.gz',
             'PB04_trimmoPE_bowtie2_notHg38.1.fastq.gz',))
        dirn = os.path.join(self.dirn,'PJB')
        project = AnalysisProject('PJB',dirn)
        self.assertEqual(project.name,'PJB')
        self.assertTrue(os.path.isdir(project.dirn))
        self.assertFalse(project.multiple_fastqs)
        self.assertFalse(project.info.paired_end)
        self.assertEqual(project.fastq_dir,
                         os.path.join(project.dirn,'fastqs'))
        self.assertEqual(project.info.samples,
                         '2 samples (PB04_S4_R1_unpaired, PB04_trimmoPE_bowtie2_notHg38.1)')
        self.assertEqual(project.fastq_dirs,['fastqs',])
        self.assertEqual(project.info.primary_fastq_dir,'fastqs')

    def test_load_analysis_project_non_with_alternative_fastq_naming(self):
        """Check AnalysisProject loading for directory with alternative fastq naming
        """
        self.make_mock_project_dir(
            'PJB',
            ('PB02.trimmed.filtered.r1.fastq.gz',
             'PB02.trimmed.filtered.r2.fastq.gz',))
        # Create a class to handle the non-canonical Fastq names
        class NonCanonicalFastq(BaseFastqAttrs):
            def __init__(self,fastq):
                BaseFastqAttrs.__init__(self,fastq)
                self.sample_name = self.basename.split('.')[0]
                self.read_number = int(self.basename.split('.')[-1][1:])
        dirn = os.path.join(self.dirn,'PJB')
        project = AnalysisProject('PJB',dirn,fastq_attrs=NonCanonicalFastq)
        self.assertEqual(project.name,'PJB')
        self.assertTrue(os.path.isdir(project.dirn))
        self.assertFalse(project.multiple_fastqs)
        self.assertTrue(project.info.paired_end)
        self.assertEqual(project.samples[0].name,'PB02')
        self.assertEqual(project.fastq_dir,
                         os.path.join(project.dirn,'fastqs'))
        self.assertEqual(project.info.samples,
                         '1 sample (PB02.trimmed.filtered)')
        self.assertEqual(project.fastq_dirs,['fastqs',])
        self.assertEqual(project.info.primary_fastq_dir,'fastqs')

    def test_load_analysis_project_detect_multiple_fastq_dirs(self):
        """Check AnalysisProject detects multiple fastqs directories
        """
        # Construct test project with two fastq subdirectories
        self.make_mock_project_dir(
            'PJB',
            ('PJB1-A_ACAGTG_L001_R1_001.fastq.gz',
             'PJB1-B_ACAGTG_L002_R1_001.fastq.gz',))
        self.make_mock_project_dir(
            'PJB.untrimmed',
            ('PJB1-A-untrimmed_ACAGTG_L001_R1_001.fastq.gz',
             'PJB1-B-untrimmed_ACAGTG_L002_R1_001.fastq.gz',),
            fastq_dir='fastqs.untrimmed')
        shutil.move(os.path.join(self.dirn,
                                 'PJB.untrimmed',
                                 'fastqs.untrimmed'),
                    os.path.join(self.dirn,'PJB'))
        shutil.rmtree(os.path.join(self.dirn,'PJB.untrimmed'))
        # Load and check AnalysisProject: default fastqs dir
        dirn = os.path.join(self.dirn,'PJB')
        project = AnalysisProject('PJB',dirn)
        self.assertEqual(project.name,'PJB')
        self.assertTrue(os.path.isdir(project.dirn))
        self.assertFalse(project.multiple_fastqs)
        self.assertFalse(project.info.paired_end)
        self.assertEqual(project.samples[0].name,'PJB1-A')
        self.assertEqual(project.samples[1].name,'PJB1-B')
        self.assertEqual(project.fastq_dir,
                         os.path.join(project.dirn,'fastqs'))
        self.assertEqual(project.info.samples,'2 samples (PJB1-A, PJB1-B)')
        self.assertEqual(project.fastq_dirs,
                         ['fastqs','fastqs.untrimmed'])
        # Load and check AnalysisProject: default fastqs dir
        dirn = os.path.join(self.dirn,'PJB')
        project = AnalysisProject('PJB',dirn,
                                  fastq_dir='fastqs.untrimmed')
        self.assertEqual(project.name,'PJB')
        self.assertTrue(os.path.isdir(project.dirn))
        self.assertFalse(project.multiple_fastqs)
        self.assertFalse(project.info.paired_end)
        self.assertEqual(project.samples[0].name,'PJB1-A-untrimmed')
        self.assertEqual(project.samples[1].name,'PJB1-B-untrimmed')
        self.assertEqual(project.fastq_dir,
                         os.path.join(project.dirn,'fastqs.untrimmed'))
        self.assertEqual(project.info.samples,'2 samples (PJB1-A, PJB1-B)')
        self.assertEqual(project.fastq_dirs,
                         ['fastqs','fastqs.untrimmed'])
        self.assertEqual(project.info.primary_fastq_dir,'fastqs')

    def test_analysis_project_switch_fastq_dir(self):
        """Check AnalysisProject can switch between multiple fastqs directories
        """
        # Construct test project with two fastq subdirectories
        self.make_mock_project_dir(
            'PJB',
            ('PJB1-A_ACAGTG_L001_R1_001.fastq.gz',
             'PJB1-B_ACAGTG_L002_R1_001.fastq.gz',))
        self.make_mock_project_dir(
            'PJB.untrimmed',
            ('PJB1-A-untrimmed_ACAGTG_L001_R1_001.fastq.gz',
             'PJB1-B-untrimmed_ACAGTG_L002_R1_001.fastq.gz',),
            fastq_dir='fastqs.untrimmed')
        shutil.move(os.path.join(self.dirn,
                                 'PJB.untrimmed',
                                 'fastqs.untrimmed'),
                    os.path.join(self.dirn,'PJB'))
        shutil.rmtree(os.path.join(self.dirn,'PJB.untrimmed'))
        # Load and check AnalysisProject: default fastqs dir
        dirn = os.path.join(self.dirn,'PJB')
        project = AnalysisProject('PJB',dirn)
        self.assertEqual(project.name,'PJB')
        self.assertTrue(os.path.isdir(project.dirn))
        self.assertFalse(project.multiple_fastqs)
        self.assertFalse(project.info.paired_end)
        self.assertEqual(project.samples[0].name,'PJB1-A')
        self.assertEqual(project.samples[1].name,'PJB1-B')
        self.assertEqual(project.fastq_dir,
                         os.path.join(project.dirn,'fastqs'))
        self.assertEqual(project.fastq_dirs,
                         ['fastqs','fastqs.untrimmed'])
        # Switch to alternative fastqs dir
        project.use_fastq_dir('fastqs.untrimmed')
        self.assertEqual(project.name,'PJB')
        self.assertTrue(os.path.isdir(project.dirn))
        self.assertFalse(project.multiple_fastqs)
        self.assertFalse(project.info.paired_end)
        self.assertEqual(project.samples[0].name,'PJB1-A-untrimmed')
        self.assertEqual(project.samples[1].name,'PJB1-B-untrimmed')
        self.assertEqual(project.fastq_dir,
                         os.path.join(project.dirn,'fastqs.untrimmed'))
        self.assertEqual(project.info.samples,'2 samples (PJB1-A, PJB1-B)')
        self.assertEqual(project.fastq_dirs,
                         ['fastqs','fastqs.untrimmed'])
        self.assertEqual(project.info.primary_fastq_dir,'fastqs')

    def test_analysis_project_switch_to_default_fastq_dir(self):
        """Check AnalysisProject switches to default fastq set
        """
        # Construct test project with two fastq subdirectories
        self.make_mock_project_dir(
            'PJB',
            ('PJB1-A_ACAGTG_L001_R1_001.fastq.gz',
             'PJB1-B_ACAGTG_L002_R1_001.fastq.gz',))
        self.make_mock_project_dir(
            'PJB.untrimmed',
            ('PJB1-A-untrimmed_ACAGTG_L001_R1_001.fastq.gz',
             'PJB1-B-untrimmed_ACAGTG_L002_R1_001.fastq.gz',),
            fastq_dir='fastqs.untrimmed')
        shutil.move(os.path.join(self.dirn,
                                 'PJB.untrimmed',
                                 'fastqs.untrimmed'),
                    os.path.join(self.dirn,'PJB'))
        shutil.rmtree(os.path.join(self.dirn,'PJB.untrimmed'))
        # Load and check AnalysisProject with alternative fastq set
        dirn = os.path.join(self.dirn,'PJB')
        project = AnalysisProject('PJB',dirn,fastq_dir='fastqs.untrimmed')
        self.assertEqual(project.name,'PJB')
        self.assertTrue(os.path.isdir(project.dirn))
        self.assertFalse(project.multiple_fastqs)
        self.assertFalse(project.info.paired_end)
        self.assertEqual(project.samples[0].name,'PJB1-A-untrimmed')
        self.assertEqual(project.samples[1].name,'PJB1-B-untrimmed')
        self.assertEqual(project.fastq_dir,
                         os.path.join(project.dirn,'fastqs.untrimmed'))
        self.assertEqual(project.info.samples,'2 samples (PJB1-A, PJB1-B)')
        self.assertEqual(project.fastq_dirs,
                         ['fastqs','fastqs.untrimmed'])
        self.assertEqual(project.info.primary_fastq_dir,'fastqs')
        # Implicitly switch to primary fastq set
        project.use_fastq_dir()
        self.assertEqual(project.name,'PJB')
        self.assertTrue(os.path.isdir(project.dirn))
        self.assertFalse(project.multiple_fastqs)
        self.assertFalse(project.info.paired_end)
        self.assertEqual(project.samples[0].name,'PJB1-A')
        self.assertEqual(project.samples[1].name,'PJB1-B')
        self.assertEqual(project.fastq_dir,
                         os.path.join(project.dirn,'fastqs'))
        self.assertEqual(project.info.samples,'2 samples (PJB1-A, PJB1-B)')
        self.assertEqual(project.fastq_dirs,
                         ['fastqs','fastqs.untrimmed'])
        self.assertEqual(project.info.primary_fastq_dir,'fastqs')

    def test_analysis_project_switch_to_default_non_canonical_fastq_dir(self):
        """Check AnalysisProject switches to default (non-canonical) fastq set
        """
        # Construct test project with two fastq subdirectories
        # and make non-canonical named primary set
        self.make_mock_project_dir(
            'PJB',
            ('PJB1-A-untrimmed_ACAGTG_L001_R1_001.fastq.gz',
             'PJB1-B-untrimmed_ACAGTG_L002_R1_001.fastq.gz',),
            fastq_dir='fastqs.untrimmed')
        self.make_mock_project_dir(
            'PJB.trimmed',
            ('PJB1-A_ACAGTG_L001_R1_001.fastq.gz',
             'PJB1-B_ACAGTG_L002_R1_001.fastq.gz',))
        shutil.move(os.path.join(self.dirn,
                                 'PJB.trimmed',
                                 'fastqs'),
                    os.path.join(self.dirn,'PJB'))
        shutil.rmtree(os.path.join(self.dirn,'PJB.trimmed'))
        # Load and check AnalysisProject primary fastq set
        dirn = os.path.join(self.dirn,'PJB')
        project = AnalysisProject('PJB',dirn)
        self.assertEqual(project.info.primary_fastq_dir,'fastqs.untrimmed')
        self.assertEqual(project.fastq_dir,
                         os.path.join(project.dirn,'fastqs.untrimmed'))
        self.assertEqual(project.info.samples,
                         '2 samples (PJB1-A-untrimmed, PJB1-B-untrimmed)')
        # Load again with alternative fastq set
        project = AnalysisProject('PJB',dirn,fastq_dir='fastqs')
        self.assertEqual(project.info.primary_fastq_dir,'fastqs.untrimmed')
        self.assertEqual(project.fastq_dir,
                         os.path.join(project.dirn,'fastqs'))
        self.assertEqual(project.info.samples,
                         '2 samples (PJB1-A-untrimmed, PJB1-B-untrimmed)')
        # Implicitly switch to primary fastq set
        project.use_fastq_dir()
        self.assertEqual(project.info.primary_fastq_dir,'fastqs.untrimmed')
        self.assertEqual(project.fastq_dir,
                         os.path.join(project.dirn,'fastqs.untrimmed'))
        self.assertEqual(project.info.samples,
                         '2 samples (PJB1-A-untrimmed, PJB1-B-untrimmed)')

    def test_analysis_project_update_primary_fastq_dir(self):
        """Check AnalysisProject primary fastq set can be updated
        """
        # Construct test project with two fastq subdirectories
        self.make_mock_project_dir(
            'PJB',
            ('PJB1-A_ACAGTG_L001_R1_001.fastq.gz',
             'PJB1-B_ACAGTG_L002_R1_001.fastq.gz',))
        self.make_mock_project_dir(
            'PJB.untrimmed',
            ('PJB1-A-untrimmed_ACAGTG_L001_R1_001.fastq.gz',
             'PJB1-B-untrimmed_ACAGTG_L002_R1_001.fastq.gz',),
            fastq_dir='fastqs.untrimmed')
        shutil.move(os.path.join(self.dirn,
                                 'PJB.untrimmed',
                                 'fastqs.untrimmed'),
                    os.path.join(self.dirn,'PJB'))
        shutil.rmtree(os.path.join(self.dirn,'PJB.untrimmed'))
        # Load and check AnalysisProject primary fastq set
        dirn = os.path.join(self.dirn,'PJB')
        project = AnalysisProject('PJB',dirn)
        self.assertEqual(project.info.primary_fastq_dir,'fastqs')
        self.assertEqual(project.info.samples,'2 samples (PJB1-A, PJB1-B)')
        self.assertEqual(project.fastq_dir,
                         os.path.join(project.dirn,'fastqs'))
        self.assertEqual(project.fastq_dirs,['fastqs','fastqs.untrimmed'])
        # Update the primary fastq set
        project.set_primary_fastq_dir('fastqs.untrimmed')
        self.assertEqual(project.info.primary_fastq_dir,'fastqs.untrimmed')
        self.assertEqual(project.fastq_dir,
                         os.path.join(project.dirn,'fastqs'))
        self.assertEqual(project.info.samples,
                         '2 samples (PJB1-A-untrimmed, PJB1-B-untrimmed)')
        self.assertEqual(project.fastq_dirs,['fastqs','fastqs.untrimmed'])
        # Reload the project and check that the change has stuck
        project1 = AnalysisProject('PJB',dirn)
        self.assertEqual(project1.info.primary_fastq_dir,'fastqs.untrimmed')
        self.assertEqual(project1.fastq_dir,
                         os.path.join(project.dirn,'fastqs.untrimmed'))
        self.assertEqual(project1.fastq_dirs,['fastqs','fastqs.untrimmed'])
        self.assertEqual(project1.info.samples,
                         '2 samples (PJB1-A-untrimmed, PJB1-B-untrimmed)')

    def test_analysis_project_switch_to_non_existant_fastq_dir(self):
        """Check AnalysisProject fails when switching to non-existant fastqs dir
        """
        self.make_mock_project_dir(
            'PJB',
            ('PJB1-A_ACAGTG_L001_R1_001.fastq.gz',
             'PJB1-B_ACAGTG_L002_R1_001.fastq.gz',))
        dirn = os.path.join(self.dirn,'PJB')
        project = AnalysisProject('PJB',dirn)
        self.assertRaises(Exception,
                          project.use_fastq_dir,'fastqs.non_existant')

    def test_sample_summary_single_ended(self):
        """AnalysisProject: sample_summary works for SE data
        """
        self.make_mock_project_dir(
            'PJB',
            ('PJB1-A_ACAGTG_L001_R1_001.fastq.gz',
             'PJB1-B_ACAGTG_L002_R1_001.fastq.gz',))
        project = AnalysisProject('PJB',os.path.join(self.dirn,'PJB'))
        self.assertEqual(project.sample_summary(),
                         "2 samples (PJB1-A, PJB1-B)")

    def test_sample_summary_paired_ended(self):
        """AnalysisProject: sample_summary works for PE data
        """
        self.make_mock_project_dir(
            'PJB',
            ('PJB1-A_ACAGTG_L001_R1_001.fastq.gz',
             'PJB1-A_ACAGTG_L001_R2_001.fastq.gz',
             'PJB1-B_ACAGTG_L002_R1_001.fastq.gz',
             'PJB1-B_ACAGTG_L002_R2_001.fastq.gz',))
        project = AnalysisProject('PJB',os.path.join(self.dirn,'PJB'))
        self.assertEqual(project.sample_summary(),
                         "2 samples (PJB1-A, PJB1-B)")

    def test_sample_summary_single_ended_multiple_fastqs(self):
        """AnalysisProject: sample_summary works for SE data, multiple fastqs
        """
        self.make_mock_project_dir(
            'PJB',
            ('PJB1-A_ACAGTG_L001_R1_001.fastq.gz',
             'PJB1-A_ACAGTG_L002_R1_001.fastq.gz',
             'PJB1-B_ACAGTG_L001_R1_001.fastq.gz',
             'PJB1-B_ACAGTG_L002_R1_001.fastq.gz',))
        project = AnalysisProject('PJB',os.path.join(self.dirn,'PJB'))
        self.assertEqual(project.sample_summary(),
                         "2 samples (PJB1-A, PJB1-B, multiple fastqs per sample)")

    def test_sample_summary_paired_ended_multiple_fastqs(self):
        """AnalysisProject: sample_summary works for PE data, multiple fastqs
        """
        self.make_mock_project_dir(
            'PJB',
            ('PJB1-A_ACAGTG_L001_R1_001.fastq.gz',
             'PJB1-A_ACAGTG_L001_R2_001.fastq.gz',
             'PJB1-A_ACAGTG_L002_R1_001.fastq.gz',
             'PJB1-A_ACAGTG_L002_R2_001.fastq.gz',
             'PJB1-B_ACAGTG_L001_R1_001.fastq.gz',
             'PJB1-B_ACAGTG_L002_R2_001.fastq.gz',
             'PJB1-B_ACAGTG_L001_R1_001.fastq.gz',
             'PJB1-B_ACAGTG_L002_R2_001.fastq.gz',))
        project = AnalysisProject('PJB',os.path.join(self.dirn,'PJB'))
        self.assertEqual(project.sample_summary(),
                         "2 samples (PJB1-A, PJB1-B, multiple fastqs per sample)")

    def test_sample_summary_paired_ended_ignore_index_reads(self):
        """AnalysisProject: sample_summary works for PE data with index reads
        """
        self.make_mock_project_dir(
            'PJB',
            ('PJB1-A_ACAGTG_L001_R1_001.fastq.gz',
             'PJB1-A_ACAGTG_L001_R2_001.fastq.gz',
             'PJB1-A_ACAGTG_L001_I1_001.fastq.gz',
             'PJB1-B_ACAGTG_L002_R1_001.fastq.gz',
             'PJB1-B_ACAGTG_L002_R2_001.fastq.gz',
             'PJB1-B_ACAGTG_L002_I1_001.fastq.gz',))
        project = AnalysisProject('PJB',os.path.join(self.dirn,'PJB'))
        self.assertEqual(project.sample_summary(),
                         "2 samples (PJB1-A, PJB1-B)")

    def test_sample_summary_no_samples(self):
        """AnalysisProject: sample_summary works when there are no samples
        """
        self.make_mock_project_dir('PJB',())
        project = AnalysisProject('PJB',os.path.join(self.dirn,'PJB'))
        self.assertEqual(project.sample_summary(),"No samples")

class TestAnalysisSample(unittest.TestCase):
    """Tests for the AnalysisSample class

    """

    def test_empty_analysis_sample(self):
        """Check empty AnalysisSample class
        """
        sample = AnalysisSample('PJB1-A')
        self.assertEqual(sample.name,'PJB1-A')
        self.assertEqual(sample.fastq,[])
        self.assertFalse(sample.paired_end)
        self.assertEqual(str(sample),'PJB1-A')

    def test_single_end_analysis_sample(self):
        """Check AnalysisSample class with single-end sample
        """
        fq = '/run/sample1/PJB1-B_ACAGTG_L001_R1.fastq.gz'
        sample = AnalysisSample('PJB1-B')
        sample.add_fastq(fq)
        self.assertEqual(sample.name,'PJB1-B')
        self.assertEqual(sample.fastq,[fq])
        self.assertEqual(sample.fastq_subset(read_number=1),[fq])
        self.assertEqual(sample.fastq_subset(read_number=2),[])
        self.assertFalse(sample.paired_end)
        self.assertEqual(str(sample),'PJB1-B')

    def test_single_end_analysis_sample_multiple_fastqs(self):
        """Check AnalysisSample class with single-end sample (multiple fastqs)
        """
        sample = AnalysisSample('PJB1-B')
        fq_l1 = '/run/sample1/PJB1-B_ACAGTG_L001_R1.fastq.gz'
        fq_l2 = '/run/sample1/PJB1-B_ACAGTG_L002_R1.fastq.gz'
        sample.add_fastq(fq_l1)
        sample.add_fastq(fq_l2)
        self.assertEqual(sample.name,'PJB1-B')
        self.assertEqual(sample.fastq,[fq_l1,fq_l2])
        self.assertEqual(sample.fastq_subset(read_number=1),[fq_l1,fq_l2])
        self.assertEqual(sample.fastq_subset(read_number=2),[])
        self.assertFalse(sample.paired_end)
        self.assertEqual(str(sample),'PJB1-B')

    def test_paired_end_analysis_sample(self):
        """Check AnalysisSample class with paired-end sample
        """
        sample = AnalysisSample('PJB1-B')
        fq_r1 = '/run/sample1/PJB1-B_ACAGTG_L001_R1.fastq.gz'
        fq_r2 = '/run/sample1/PJB1-B_ACAGTG_L001_R2.fastq.gz'
        sample.add_fastq(fq_r1)
        sample.add_fastq(fq_r2)
        self.assertEqual(sample.name,'PJB1-B')
        self.assertEqual(sample.fastq,[fq_r1,fq_r2])
        self.assertEqual(sample.fastq_subset(read_number=1),[fq_r1])
        self.assertEqual(sample.fastq_subset(read_number=2),[fq_r2])

    def test_paired_end_analysis_sample_index_read_fastq(self):
        """Check AnalysisSample class with index read fastqs
        """
        sample = AnalysisSample('PJB1-B')
        fq_l1_r1 = '/run/sample1/PJB1-B_S1_L001_R1.fastq.gz'
        fq_l1_r2 = '/run/sample1/PJB1-B_S1_L001_R2.fastq.gz'
        fq_l1_i1 = '/run/sample1/PJB1-B_S1_L001_I1.fastq.gz'
        sample.add_fastq(fq_l1_r1)
        sample.add_fastq(fq_l1_r2)
        sample.add_fastq(fq_l1_i1)
        self.assertEqual(sample.name,'PJB1-B')
        self.assertEqual(sample.fastq,[fq_l1_i1,fq_l1_r1,fq_l1_r2])
        self.assertEqual(sample.fastq_subset(read_number=1),[fq_l1_r1,])
        self.assertEqual(sample.fastq_subset(read_number=2),[fq_l1_r2,])
        self.assertTrue(sample.paired_end)
        self.assertEqual(str(sample),'PJB1-B')

    def test_paired_end_analysis_sample_multiple_fastqs(self):
        """Check AnalysisSample class with paired-end sample (multiple fastqs)
        """
        sample = AnalysisSample('PJB1-B')
        fq_l1_r1 = '/run/sample1/PJB1-B_ACAGTG_L001_R1.fastq.gz'
        fq_l2_r1 = '/run/sample1/PJB1-B_ACAGTG_L002_R1.fastq.gz'
        fq_l1_r2 = '/run/sample1/PJB1-B_ACAGTG_L001_R2.fastq.gz'
        fq_l2_r2 = '/run/sample1/PJB1-B_ACAGTG_L002_R2.fastq.gz'
        sample.add_fastq(fq_l1_r1)
        sample.add_fastq(fq_l2_r1)
        sample.add_fastq(fq_l1_r2)
        sample.add_fastq(fq_l2_r2)
        self.assertEqual(sample.name,'PJB1-B')
        self.assertEqual(sample.fastq,[fq_l1_r1,fq_l1_r2,
                                       fq_l2_r1,fq_l2_r2])
        self.assertEqual(sample.fastq_subset(read_number=1),[fq_l1_r1,fq_l2_r1])
        self.assertEqual(sample.fastq_subset(read_number=2),[fq_l1_r2,fq_l2_r2])
        self.assertTrue(sample.paired_end)
        self.assertEqual(str(sample),'PJB1-B')

    def test_analysis_sample_non_canonical_fastq_naming(self):
        """Check AnalysisSample class with non-canonical fastq naming
        """
        # Create a class to handle the non-canonical Fastq names
        class NonCanonicalFastq(BaseFastqAttrs):
            def __init__(self,fastq):
                BaseFastqAttrs.__init__(self,fastq)
                self.sample_name = self.basename.split('.')[0]
                self.read_number = int(self.basename.split('.')[-1][1:])
        sample = AnalysisSample('PJB1-B',fastq_attrs=NonCanonicalFastq)
        fq_r1 = '/run/sample1/PJB1-B.ACAGTG.L001.R1.fastq.gz'
        fq_r2 = '/run/sample1/PJB1-B.ACAGTG.L001.R2.fastq.gz'
        sample.add_fastq(fq_r1)
        sample.add_fastq(fq_r2)
        self.assertEqual(sample.name,'PJB1-B')
        self.assertEqual(sample.fastq,[fq_r1,fq_r2])
        self.assertEqual(sample.fastq_subset(read_number=1),[fq_r1])
        self.assertEqual(sample.fastq_subset(read_number=2),[fq_r2])
        self.assertTrue(sample.paired_end)
        self.assertEqual(str(sample),'PJB1-B')

class TestZipArchive(unittest.TestCase):
    """
    Tests for the ZipArchive class
    """
    def setUp(self):
        self.dirn = tempfile.mkdtemp(suffix='TestZipArchive')

    def tearDown(self):
        # Remove the temporary test directory
        shutil.rmtree(self.dirn)

    def test_create_zip_archive(self):
        """ZipArchive: create a new zip archive
        """
        # Make an example directory to zip up
        src_dir = os.path.join(self.dirn,'source')
        items = ('test1',
                 'test2',
                 'sub1/',
                 'sub1/test3',
                 'sub1/test4',
                 'sub1/sub2/',
                 'sub1/sub2/test5',
                 'sub3/',
                 'sub3/test6')
        os.mkdir(src_dir)
        for item in [os.path.join(self.dirn,x) for x in items]:
            if item.endswith('/'):
                try:
                    os.mkdir(item)
                except OSError as ex:
                    raise OSError("Failed to make %s" % item)
            else:
                open(item,'w').write('')
        # Create the zip archive
        zip_filename = os.path.join(self.dirn,'test.zip')
        self.assertFalse(os.path.exists(zip_filename))
        z = ZipArchive(zip_filename,relpath=self.dirn)
        for item in [os.path.join(self.dirn,x) for x in ('test1','sub1')]:
            z.add(item)
        z.close()
        # Check the zip archive exists
        self.assertTrue(os.path.exists(zip_filename),
                        "zip file not created")
        self.assertTrue(zipfile.is_zipfile(zip_filename),
                        "file exists but is not zip file")
        # Check the contents
        namelist = zipfile.ZipFile(zip_filename).namelist()
        print namelist
        for item in ('test1',
                     'sub1/test3',
                     'sub1/test4',
                     'sub1/sub2/test5'):
            self.assertTrue((item.rstrip('/') in namelist),
                            "Item '%s' not in zip file" % item)
        for name in namelist:
            self.assertTrue((name in ('test1',
                                      'sub1/test3',
                                      'sub1/test4',
                                      'sub1/sub2/test5')),
                            "'%s' in zip file but shouldn't be"
                            % name)

class TestOutputFiles(unittest.TestCase):
    """
    Tests for the OutputFiles class
    """
    def setUp(self):
        # Temporary working dir
        self.wd = tempfile.mkdtemp(suffix='.test_outputfile')
    def tearDown(self):
        # Remove temporary working dir
        if os.path.isdir(self.wd):
            shutil.rmtree(self.wd)
    def test_outputfiles(self):
        out = OutputFiles()
        out.open('test1',os.path.join(self.wd,'test1.txt'))
        out.open('test2',os.path.join(self.wd,'test2.txt'))
        self.assertEqual(
            out.file_name('test1'),os.path.join(self.wd,'test1.txt'))
        self.assertEqual(
            out.file_name('test2'),os.path.join(self.wd,'test2.txt'))
        out.write('test1','Some test text')
        out.write('test2','Some more\ntest text')
        out.close()
        self.assertEqual(open(out.file_name('test1'),'r').read(),
                         "Some test text\n")
        self.assertEqual(open(out.file_name('test2'),'r').read(),
                         "Some more\ntest text\n")
    def test_outputfiles_with_basedir(self):
        out = OutputFiles(self.wd)
        out.open('test1','test1.txt')
        out.open('test2','test2.txt')
        self.assertEqual(
            out.file_name('test1'),os.path.join(self.wd,'test1.txt'))
        self.assertEqual(
            out.file_name('test2'),os.path.join(self.wd,'test2.txt'))
    def test_outputfiles_contains(self):
        out = OutputFiles()
        out.open('test1',os.path.join(self.wd,'test1.txt'))
        self.assertTrue('test1' in out)
        self.assertFalse('test2' in out)
        out.close()
        self.assertFalse('test1' in out)
        self.assertEqual(out.file_name('test1'),
                         os.path.join(self.wd,'test1.txt'))
        self.assertFalse('test2' in out)
        self.assertRaises(KeyError,out.file_name,'test2')
    def test_outputfiles_append(self):
        out = OutputFiles()
        with open(os.path.join(self.wd,'test1.txt'),'w') as fp:
            fp.write("test1 already exists\n")
        with open(os.path.join(self.wd,'test2.txt'),'w') as fp:
            fp.write("test2 already exists\n")
        out.open('test1',os.path.join(self.wd,'test1.txt'),append=True)
        out.open('test2',os.path.join(self.wd,'test2.txt'))
        self.assertEqual(
            out.file_name('test1'),os.path.join(self.wd,'test1.txt'))
        self.assertEqual(
            out.file_name('test2'),os.path.join(self.wd,'test2.txt'))
        out.write('test1','Some test text')
        out.write('test2','Some more\ntest text')
        out.close()
        self.assertEqual(open(out.file_name('test1'),'r').read(),
                         "test1 already exists\nSome test text\n")
        self.assertEqual(open(out.file_name('test2'),'r').read(),
                         "Some more\ntest text\n")
    def test_outputfiles_reopen(self):
        out = OutputFiles(base_dir=self.wd)
        out.open('test1','test1.txt')
        out.open('test2','test2.txt')
        self.assertEqual(out.file_name('test1'),
                         os.path.join(self.wd,'test1.txt'))
        self.assertEqual(out.file_name('test2'),
                         os.path.join(self.wd,'test2.txt'))
        out.write('test1','Some test text')
        out.write('test2','Some more\ntest text')
        out.close()
        self.assertEqual(open(out.file_name('test1'),'r').read(),
                         "Some test text\n")
        self.assertEqual(open(out.file_name('test2'),'r').read(),
                         "Some more\ntest text\n")
        # Reopen files
        out.open('test1',append=True)
        out.open('test2')
        self.assertEqual(out.file_name('test1'),
                         os.path.join(self.wd,'test1.txt'))
        self.assertEqual(out.file_name('test2'),
                         os.path.join(self.wd,'test2.txt'))
        out.write('test1','Some extra test text')
        out.write('test2','Some different\ntest text')
        out.close()
        self.assertEqual(open(out.file_name('test1'),'r').read(),
                         "Some test text\nSome extra test text\n")
        self.assertEqual(open(out.file_name('test2'),'r').read(),
                         "Some different\ntest text\n")
    def test_outputfiles_len(self):
        out = OutputFiles(base_dir=self.wd)
        self.assertEqual(len(out),0)
        out.open('test1','test1.txt')
        self.assertEqual(len(out),1)
        out.close('test1')
        self.assertEqual(len(out),0)
        out.open('test2','test2.txt')
        out.open('test3','test3.txt')
        self.assertEqual(len(out),2)
        out.open('test1',append=True)
        self.assertEqual(len(out),3)
        out.close()
        self.assertEqual(len(out),0)
        out.open('test2',append=True)
        self.assertEqual(len(out),1)

class TestShowProgressChecker(unittest.TestCase):
    """
    Tests for the ProgressChecker class
    """
    def test_check_progress_every(self):
        """
        ProgressChecker: check every N items
        """
        progress = ProgressChecker(every=1)
        self.assertTrue(progress.check(0))
        self.assertTrue(progress.check(1))
        progress = ProgressChecker(every=5)
        self.assertTrue(progress.check(0))
        self.assertFalse(progress.check(1))
        self.assertTrue(progress.check(5))
        self.assertTrue(progress.check(20))
        self.assertFalse(progress.check(21))
    def test_check_progress_every_percent(self):
        """
        ProgressChecker: check every percentage of items
        """
        progress = ProgressChecker(percent=5,total=12209)
        self.assertTrue(progress.check(0))
        self.assertFalse(progress.check(1))
        self.assertFalse(progress.check(609))
        self.assertTrue(progress.check(610))
    def test_check_progress_every_percent_zero_total(self):
        """
        ProgressChecker: supplied total is zero for percentage
        """
        progress = ProgressChecker(percent=5,total=0)
        self.assertFalse(progress.check(0))
    def test_check_progress_every_percent_zero_total(self):
        """
        ProgressChecker: supplied total is smaller than percentage
        """
        progress = ProgressChecker(percent=10,total=9)
        self.assertTrue(progress.check(0))
        self.assertTrue(progress.check(1))
    def test_get_percentage(self):
        """
        ProgressChecker: check returned percentage
        """
        progress = ProgressChecker(percent=5,total=12209)
        self.assertEqual(progress.percent(0),float(0))
        self.assertEqual(progress.percent(610),610.0/12209.0*100.0)
        self.assertEqual(progress.percent(12209),float(100))

class TestBasesMaskIsPairedEnd(unittest.TestCase):
    """Tests for the bases_mask_is_paired_end function

    """

    def test_single_end_bases_mask(self):
        """Check examples of single-ended bases masks
        """
        self.assertFalse(bases_mask_is_paired_end('y36'))
        self.assertFalse(bases_mask_is_paired_end('y50,I6'))
        self.assertFalse(bases_mask_is_paired_end('y50,I6n'))

    def test_paired_end_bases_mask(self):
        """Check examples of single-ended bases masks
        """
        self.assertTrue(bases_mask_is_paired_end('y101,I6n,y101'))
        self.assertTrue(bases_mask_is_paired_end('y101,I6,I6,y101'))

class TestSplitUserHostDir(unittest.TestCase):
    """Tests for the split_user_host_dir function

    """

    def test_user_host_dir(self):
        """Check we can split user@host.name:/path/to/somewhere
        """
        user,host,dirn = split_user_host_dir('user@host.name:/path/to/somewhere')
        self.assertEqual(user,'user')
        self.assertEqual(host,'host.name')
        self.assertEqual(dirn,'/path/to/somewhere')

    def test_host_dir(self):
        """Check we can split host.name:/path/to/somewhere
        """
        user,host,dirn = split_user_host_dir('host.name:/path/to/somewhere')
        self.assertEqual(user,None)
        self.assertEqual(host,'host.name')
        self.assertEqual(dirn,'/path/to/somewhere')

    def test_dir(self):
        """Check we can 'split' /path/to/somewhere
        """
        user,host,dirn = split_user_host_dir('/path/to/somewhere')
        self.assertEqual(user,None)
        self.assertEqual(host,None)
        self.assertEqual(dirn,'/path/to/somewhere')

    def test_extra_whitespace(self):
        """Check we can handle additional leading/trailing whitespace
        """
        user,host,dirn = split_user_host_dir('\tuser@host.name:/path/to/somewhere  \n')
        self.assertEqual(user,'user')
        self.assertEqual(host,'host.name')
        self.assertEqual(dirn,'/path/to/somewhere')

    def test_bad_input(self):
        """Check that empty string or None return sensible values
        """
        user,host,dirn = split_user_host_dir('')
        self.assertEqual(user,None)
        self.assertEqual(host,None)
        self.assertEqual(dirn,None)
        user,host,dirn = split_user_host_dir(None)
        self.assertEqual(user,None)
        self.assertEqual(host,None)
        self.assertEqual(dirn,None)

class TestGetNumberedSubdir(unittest.TestCase):
    """
    Tests for the 'get_numbered_subdir' function
    """
    def setUp(self):
        # Make temporary working dir
        self.wd = tempfile.mkdtemp(suffix="TestGetNumberedSubdir")
        # Store cwd
        self.original_dir = os.getcwd()
    def tearDown(self):
        # Restore origin cwd
        os.chdir(self.original_dir)
        # Remove working dir
        shutil.rmtree(self.wd)
    def test_get_numbered_subdir(self):
        """
        get_numbered_subdir: first subdir in parent
        """
        self.assertEqual(
            get_numbered_subdir("test",parent_dir=self.wd),
            "001_test")
    def test_get_numbered_subdir_next_in_sequence(self):
        """
        get_numbered_subdir: next subdir in sequence
        """
        for d in ("001_test","002_test"):
            os.mkdir(os.path.join(self.wd,d))
        self.assertEqual(
            get_numbered_subdir("test",parent_dir=self.wd),
            "003_test")
    def test_get_numbered_subdir_ignore_gaps(self):
        """
        get_numbered_subdir: ignore gaps in sequence
        """
        for d in ("001_test","003_test"):
            os.mkdir(os.path.join(self.wd,d))
        self.assertEqual(
            get_numbered_subdir("test",parent_dir=self.wd),
            "004_test")
    def test_get_numbered_subdir_default_to_cwd(self):
        """
        get_numbered_subdir: parent defaults to CWD
        """
        test_dir1 = os.path.join(self.wd,"test1")
        os.mkdir(test_dir1)
        for d in ("001_test","002_test"):
            os.mkdir(os.path.join(test_dir1,d))
        os.chdir(test_dir1)
        self.assertEqual(
            get_numbered_subdir("test"),"003_test")
        test_dir2 = os.path.join(self.wd,"test2")
        os.mkdir(test_dir2)
        os.chdir(test_dir2)
        self.assertEqual(
            get_numbered_subdir("test"),"001_test")
    def test_get_numbered_subdir_full_path(self):
        """
        get_numbered_subdir: return full path
        """
        self.assertEqual(
            get_numbered_subdir("test",
                                parent_dir=self.wd,
                                full_path=True),
            os.path.join(self.wd,"001_test"))

class TestFindExecutables(unittest.TestCase):
    """
    Tests for the find_executables function

    """
    def setUp(self):
        # Make temporary working dir
        self.wd = tempfile.mkdtemp(suffix="TestCellrangerInfo")
        # Store the original state of PATH env var
        self.original_path = os.environ['PATH']
        # Info function
        def info_func(p):
            name = os.path.basename(p)
            exe = find_program(p)
            version = ''
            output = Command(exe).subprocess_check_output()[1]
            for line in output.split('\n'):
                if line.startswith(name):
                    try:
                        version = line.split()[1]
                    except IndexError:
                        pass
                    break
            return (exe,name.upper(),version)
        self.info_func = info_func

    def tearDown(self):
        # Restore the PATH env var
        os.environ['PATH'] = self.original_path
        # Remove temp dir
        shutil.rmtree(self.wd)

    def _make_executable(self,name,dirn=None,version=None):
        # Create an executable for testing
        # The executable will be created in the working dir,
        # optionally under the specified subdir
        if dirn is not None:
            path = self.wd
            for d in dirn.split(os.sep):
                path = os.path.join(path,d)
                os.mkdir(path)
            dirn = path
        else:
            dirn = self.wd
        exe = os.path.join(dirn,name)
        with open(exe,'w') as fp:
            fp.write(
                "#!/bin/bash\necho %s %s" %
                (name,
                 (version if version is not None else "")))
        os.chmod(exe,0775)
        return exe

    def _info_func(self):
        # Create an info_func for testing
        def info_func(p):
            name = os.path.basename(p)
            exe = find_program(p)
            version = ''
            output = Command(exe).subprocess_check_output()[1]
            for line in output.split('\n'):
                if line.startswith(name):
                    try:
                        version = line.split()[1]
                    except IndexError:
                        pass
                    break
            return (exe,name.upper(),version)
        return info_func

    def _prepend_path(self,p):
        # Add to start of PATH
        os.environ['PATH'] = "%s:%s" % (p,os.environ['PATH'])

    def test_no_versions(self):
        """
        find_executables: no matching software present
        """
        os.environ['PATH'] = ''
        self.assertEqual(find_executables(("xyxyz",),self.info_func),[])

    def test_single_version(self):
        """
        find_executable: only single version available
        """
        xyxyz = self._make_executable("xyxyz",version="1.0.0")
        self._prepend_path(os.path.dirname(xyxyz))
        self.assertEqual(find_executables(("xyxyz",),self._info_func()),[xyxyz,])
    def test_multiple_versions(self):
        """
        find_executable: multiple versions available
        """
        exes = []
        for v in ('2.0.0','1.2.1','1.0.0'):
            exe = self._make_executable("xyxyz",
                                        dirn="%s/bin" % v,
                                        version=v)
            exes.insert(0,exe)
            self._prepend_path(os.path.dirname(exe))
        self.assertEqual(find_executables(("xyxyz",),self._info_func()),exes)

    def test_require_specific_version(self):
        """
        find_executable: require specific version
        """
        exes = []
        for v in ('2.0.0','1.2.1','1.0.0'):
            exe = self._make_executable("xyxyz",
                                        dirn="%s/bin" % v,
                                        version=v)
            if v == '1.2.1':
                exes.append(exe)
            self._prepend_path(os.path.dirname(exe))
        self.assertEqual(find_executables(("xyxyz",),
                                          self._info_func(),
                                          reqs='1.2.1'),exes)

    def test_required_version_not_found(self):
        """
        find_executable: required version is not found
        """
        for v in ('2.0.0','1.2.1','1.0.0'):
            exe = self._make_executable("xyxyz",
                                        dirn="%s/bin" % v,
                                        version=v)
            self._prepend_path(os.path.dirname(exe))
        self.assertEqual(find_executables(("xyxyz",),
                                          self._info_func(),
                                          reqs='2.0.1'),[])

    def test_multiple_exes(self):
        """
        find_executable: look for multiple executables
        """
        exes = []
        names = ('xyxyz','zyzyx','pqrst')
        for n in names:
            exe = self._make_executable(n)
            if n != 'pqrst':
                exes.insert(0,exe)
        self._prepend_path(self.wd)
        self.assertEqual(find_executables(("zyzyx","xyxyz",),
                                          self._info_func()),exes)

    def test_specify_path(self):
        """
        find_executable: look for multiple executables
        """
        exes = []
        paths = []
        names = ('xyxyz','zyzyx','pqrst')
        for n in names:
            exe = self._make_executable(n,dirn=n)
            if n == 'zyzyx':
                exes.append(exe)
                paths.append(os.path.dirname(exe))
            self._prepend_path(os.path.dirname(exe))
        print os.environ['PATH']
        self.assertEqual(find_executables(("zyzyx","xyxyz",),
                                          self.info_func,
                                          paths=paths),exes)

class TestParseVersion(unittest.TestCase):
    """Tests for the parse_version function
    """
    def test_parse_version(self):
        """parse_version splits version numbers
        """
        self.assertEqual(parse_version("2.17.1.4"),
                         (2,17,1,4))
        self.assertEqual(parse_version("1.8.4"),
                         (1,8,4))
        self.assertEqual(parse_version("1.9.rc1"),
                         (1,9,"rc1"))

    def test_compare_versions(self):
        """parse_version compares versions correctly
        """
        self.assertTrue(
            parse_version("2.17.1.4") > parse_version("1.8.4"))
        self.assertTrue(
            parse_version("2.17.1.4") == parse_version("2.17.1.4"))
        self.assertTrue(
            parse_version("1.8.4") < parse_version("2.17.1.4"))
        self.assertTrue(
            parse_version("10.0") > parse_version("9.1"))
        self.assertTrue(
            parse_version("1.10") > parse_version("1.9.rc1"))

    def test_handle_empty_version(self):
        """parse_version handles empty version
        """
        self.assertEqual(parse_version(""),(-99999,))
        self.assertTrue(
            parse_version("") < parse_version("1.8.4"))

class TestPrettyPrintRows(unittest.TestCase):
    """Tests for the pretty_print_rows function

    """
    def test_pretty_print_rows_empty_inputs(self):
        """pretty_print_rows can handle empty list
        """
        self.assertEqual(pretty_print_rows([]),"")

    def test_pretty_print_rows_single_row(self):
        """pretty_print_rows prints a single row
        """
        rows = [['hello:','A salutation']]
        self.assertEqual(pretty_print_rows(rows),
                         "hello: A salutation")

    def test_pretty_print_rows_multiple_rows(self):
        """pretty_print_rows prints multiple rows
        """
        rows = [['-','hello:','A salutation'],
                ['-','goodbye:','The End']]
        self.assertEqual(pretty_print_rows(rows),
                         "- hello:   A salutation\n- goodbye: The End     ")

    def test_pretty_print_rows_prepend(self):
        """pretty_print_rows prepend right-justifies values
        """
        rows = [['-','hello:','A salutation'],
                ['-','goodbye:','The End']]
        self.assertEqual(pretty_print_rows(rows,prepend=True),
                         "-   hello: A salutation\n- goodbye:      The End")

class TestWriteScriptFile(unittest.TestCase):
    """Tests for the write_script_file function

    """
    def setUp(self):
        self.dirn = tempfile.mkdtemp(suffix='TestWriteScripFile')

    def tearDown(self):
        # Remove the temporary test directory
        shutil.rmtree(self.dirn)

    def test_write_script_file(self):
        """write_script_file creates new script file
        """
        script_file = os.path.join(self.dirn,'test.sh')
        self.assertFalse(os.path.exists(script_file))
        write_script_file(script_file,"sleep 50\n#")
        self.assertTrue(os.path.exists(script_file))
        self.assertEqual(open(script_file).read(),
                         "sleep 50\n#\n")

    def test_write_script_file_with_shell(self):
        """write_script_file creates new script file with shell
        """
        script_file = os.path.join(self.dirn,'test.sh')
        self.assertFalse(os.path.exists(script_file))
        write_script_file(script_file,"sleep 50\n#",shell='/bin/sh')
        self.assertTrue(os.path.exists(script_file))
        self.assertEqual(open(script_file).read(),
                         "#!/bin/sh\nsleep 50\n#\n")

    def test_write_script_file_append(self):
        """write_script_file appends to an existing file
        """
        script_file = os.path.join(self.dirn,'test.sh')
        with open(script_file,'w') as fp:
            fp.write("#\necho Going to sleep\n")
        write_script_file(script_file,"sleep 50\n#",append=True)
        self.assertTrue(os.path.exists(script_file))
        self.assertEqual(open(script_file).read(),
                         "#\necho Going to sleep\nsleep 50\n#\n")
