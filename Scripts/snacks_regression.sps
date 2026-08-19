* ============================================================================
* SNACKS REGRESSION ANALYSIS - COMPREHENSIVE SPSS SYNTAX
* ============================================================================
* This syntax performs a complete regression analysis on the snacks dataset.
* Models: OLS with log-transformed DV and various predictor combinations.
* Includes diagnostics, transformations, and model comparisons.
* ============================================================================

GET FILE='Exports/snacks_regression_labeled.sav'.
EXECUTE.

* ============================================================================
* PART 1: DATA TRANSFORMATIONS
* ============================================================================
* Create log transformations for right-skewed variables.

COMPUTE ln_dollars = LN(dollars).
IF dollars <= 0 ln_dollars = $SYSMIS.

COMPUTE ln_units = LN(units).
IF units <= 0 ln_units = $SYSMIS.

COMPUTE ln_tdp = LN(tdp).
IF tdp <= 0 ln_tdp = $SYSMIS.

COMPUTE ln_of_stores = LN(of_stores).
IF of_stores <= 0 ln_of_stores = $SYSMIS.

COMPUTE ln_pct_stores_selling = LN(pct_of_stores_selling + 0.1).
IF pct_of_stores_selling <= 0 ln_pct_stores_selling = $SYSMIS.

EXECUTE.

* ============================================================================
* PART 2: DESCRIPTIVE STATISTICS & EXPLORATORY ANALYSIS
* ============================================================================

* Descriptives for key continuous variables (both raw and log-transformed).
DESCRIPTIVES VARIABLES=dollars units tdp of_stores pct_of_stores_selling
  /STATISTICS=MEAN STD MIN MAX SKEWNESS KURTOSIS.

DESCRIPTIVES VARIABLES=ln_dollars ln_units ln_tdp ln_of_stores
  /STATISTICS=MEAN STD MIN MAX SKEWNESS KURTOSIS.

* Value frequencies for categorical factors.
FREQUENCIES VARIABLES=subcategory_code unit_of_measure_code
  /FORMAT=NOTABLE /STATISTICS=MODE.

* ============================================================================
* PART 3: CORRELATIONS
* ============================================================================
* Check for multicollinearity and relationships among predictors.

CORRELATIONS
  /VARIABLES=ln_dollars ln_tdp ln_units of_stores pct_of_stores_selling
  /PRINT=TWOTAIL SIG NOSIG
  /MISSING=PAIRWISE.

* ============================================================================
* PART 4: MODEL 1 - BASELINE OLS (Log-log specification)
* ============================================================================
* DV: LN(dollars)
* Predictors: LN(tdp) + LN(units)
* This is the simplest elasticity model.

REGRESSION
  /DEPENDENT ln_dollars
  /METHOD=ENTER ln_tdp ln_units
  /STATISTICS COEFF R ANOVA COLLIN TOL SELECTION F SIG
  /SAVE PRED(pred1) RESID(resid1) COOK(cook1)
  /CRITERIA=PIN(.05) POUT(.10)
  /RESIDUALS=HISTOGRAM NORMPROB.

EXECUTE.

* ============================================================================
* PART 5: MODEL 2 - WITH CATEGORICAL FACTORS (Brand + Subcategory)
* ============================================================================
* DV: LN(dollars)
* Predictors: LN(tdp) + LN(units) + subcategory_code + unit_of_measure_code
* This captures product category and package size effects.

REGRESSION
  /DEPENDENT ln_dollars
  /METHOD=ENTER ln_tdp ln_units subcategory_code unit_of_measure_code
  /STATISTICS COEFF R ANOVA COLLIN TOL SELECTION F SIG
  /CATEGORICAL subcategory_code unit_of_measure_code
  /SAVE PRED(pred2) RESID(resid2)
  /CRITERIA=PIN(.05) POUT(.10).

EXECUTE.

* ============================================================================
* PART 6: MODEL 3 - WITH MARKET REACH VARIABLES
* ============================================================================
* DV: LN(dollars)
* Predictors: LN(tdp) + LN(units) + LN(pct_of_stores_selling) + subcategory_code
* This adds market penetration / quality signal.

REGRESSION
  /DEPENDENT ln_dollars
  /METHOD=ENTER ln_tdp ln_units ln_pct_stores_selling subcategory_code
  /STATISTICS COEFF R ANOVA COLLIN TOL SELECTION F SIG
  /CATEGORICAL subcategory_code
  /SAVE PRED(pred_m3) RESID(resid_m3)
  /CRITERIA=PIN(.05) POUT(.10).

EXECUTE.

* ============================================================================
* PART 7: MODEL 4 - INTERACTION TERM (TDP × Units)
* ============================================================================
* DV: LN(dollars)
* Predictors: LN(tdp) + LN(units) + interaction + subcategory_code
* Tests for diminishing returns or complementarity between distribution and units.

COMPUTE tdp_units_inter = ln_tdp * ln_units.
EXECUTE.

REGRESSION
  /DEPENDENT ln_dollars
  /METHOD=ENTER ln_tdp ln_units tdp_units_inter subcategory_code
  /STATISTICS COEFF R ANOVA COLLIN TOL SELECTION F SIG
  /CATEGORICAL subcategory_code
  /SAVE PRED(pred_m4) RESID(resid_m4)
  /CRITERIA=PIN(.05) POUT(.10).

EXECUTE.

* ============================================================================
* PART 8: MODEL COMPARISON (using R-squared and AIC/BIC via custom output)
* ============================================================================
* Compare the 4 models above. You can compute AIC/BIC manually if needed:
* AIC = n*ln(RSS/n) + 2*k,  where n=sample size, RSS=residual sum of squares, k=num params
* Lower AIC/BIC is better.
*
* Expected pattern:
*   - Model 1: Low R-sq (baseline, simple elasticity)
*   - Model 2: Higher R-sq (category effects add explanatory power)
*   - Model 3: Even higher (market reach variable captures penetration)
*   - Model 4: Similar or slightly better (interaction may not be significant)

TITLE 'Regression Models Summary'.
* Note: After running all models, SPSS will show R-squared in the output tables above.

* ============================================================================
* PART 9: DIAGNOSTICS FOR BEST-FIT MODEL (recommend Model 3)
* ============================================================================

* Test for heteroskedasticity (visual: residuals vs predicted scatter).
TITLE 'Model 3 Residuals vs Predicted (Heteroskedasticity Check)'.
GGRAPH
  /GRAPHDATASET NAME="graphdataset" VARIABLES=pred_m3 resid_m3 MISSING=LISTWISE
  /GRAPHSPEC CHARTTYPE=Scatter(CType=SIMPLE) MARKERSIZE=SMALL
    XVAR=NAME(pred_m3) YVAR=NAME(resid_m3).
EXECUTE.

* Test for normality of residuals.
EXAMINE VARIABLES=resid_m3
  /PLOT=HISTOGRAM NORM BOXPLOT
  /STATISTICS=DESCRIPTIVES NORMTEST(SHAPIRO).
EXECUTE.

* Identify influential observations (Cook's D > 4/n ≈ 0.00016 for n≈24k).
FILTER OFF.
USE ALL.

TITLE 'Influential Observations (Cook''s D threshold: 0.001)'.
SELECT IF (cook_m1 > 0.001).
LIST VARIABLES=upc brand dollars ln_dollars ln_tdp ln_units cook_m1.
EXECUTE.

FILTER OFF.
USE ALL.
EXECUTE.

* ============================================================================
* PART 10: SAVE FINAL RESULTS
* ============================================================================
* Save the dataset with predicted values and residuals for further analysis.

SAVE OUTFILE='Exports/snacks_regression_results.sav' /COMPRESSED.

TITLE 'Analysis Complete - Results saved to snacks_regression_results.sav'.

* ============================================================================
* RECOMMENDED NEXT STEPS IN SPSS:
* ============================================================================
* 1. Review the model outputs above to compare R-squared values.
* 2. Use the residual plots to check for heteroskedasticity or non-linearity.
* 3. Examine the normality test (Shapiro-Wilk): p > .05 suggests normality.
* 4. If heteroskedasticity is present, consider:
*    - Robust standard errors (use BOOTSTRAP in Analyze > Regression > Linear if available).
*    - Weighted least squares (WLS).
*    - Transformation of the DV (e.g., log already used; consider others).
* 5. If multicollinearity is high (VIF > 10), consider dropping or combining predictors.
* 6. Build a final model, export the regression table for reporting.
*
* VARIABLES GUIDE:
*   - ln_dollars: log(revenue) — best for modeling
*   - ln_tdp, ln_units: log-elasticity interpretation
*   - subcategory_code: product category dummy (numeric code from 1..8)
*   - unit_of_measure_code: package size dummy (numeric code)
*   - pct_of_stores_selling: % of stores carrying the product (0-100)
*   - Predicted values (pred_m1, pred_m2, pred_m3, pred_m4): use for residual plots / R-sq calc
*   - Residuals (resid_m1, resid_m2, resid_m3, resid_m4): diagnose model fit
*   - Cook's D (cook_m1): identifies influential outliers
* ============================================================================
