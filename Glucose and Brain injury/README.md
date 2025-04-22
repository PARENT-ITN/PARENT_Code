<p>The present work is part of one of the working groups of the <a href='https://parenth2020.com/'>PARENT ITN project</a>.</br>

Scripts' DOI (Zenodo): <a href='10.5281/zenodo.15033086'> 10.5281/zenodo.15033086</a></p>

<p>The scripts contained in this directory are part of the processing of data of continuous glucose measurements (CGM).
The data is not possible to be public since there is not the proper license for this.
Thus the scripts are the set of the processing functions of the CGM data.

If someone wants to use the scripts and apply the methods to their data he/she should have in mind that proper paths should be used and check for the column names as well. </p>

<p>The directory contains:
 <dl>
  <dt>GAM_code.R</dt>
  <dd>-- The script uses generalized additive models to find associations with Glucose, time, and clinical covariates.</dd>
  <dt>Hyper_And_Hypo_glycemia_time.R</dt>
  <dd>-- The script calculates the time and percentage of time a sample has some sort of hyper-/hypo- glycemia.</dd>
  <dt>Mixed_Effect_Models_rcodes.R</dt>
  <dd>-- The script uses linear mixed effect models to find if covariates and time are relevant for glucose changes.</dd>
</dl> 
</p>

<p>The <a href='https://parenth2020.com/'>PARENT project</a> has received funding from the European Union’s Horizon 2020 research and innovation programme under the Marie Sklodowska-Curie Innovative Training Network 2020. <a href='https://cordis.europa.eu/project/id/956394'>Grant Agreement N° 956394</a></p>