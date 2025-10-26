"""
CARIBBEAN BUDGET INTELLIGENCE™
Budget Intelligence Index (BII) Calculator
Version: 1.0.0
"""

from dataclasses import dataclass
from typing import Dict, Tuple
import math

@dataclass
class LayerInputs:
    """Input data for all 9 layers"""
    # Layer 1: Fiscal Transparency
    budget_on_time: bool
    audit_delay_years: int
    
    # Layer 2: Revenue Stability
    non_oil_revenue_percent: float
    tax_base_breadth_score: float  # 0-10
    collection_efficiency: float    # 0-10
    
    # Layer 3: Public Debt Health
    debt_to_gdp: float
    debt_service_to_revenue: float
    fiscal_balance_trend: str  # "improving", "stable", "declining"
    
    # Layer 4: Expenditure Efficiency
    productive_spending_percent: float  # education, infrastructure, agriculture
    consumption_spending_percent: float # subsidies, debt service
    
    # Layer 5: Private Sector Climate
    ease_of_business_rank: int  # Out of 190
    sme_support_delivery_rate: float  # 0-100%
    forex_access_score: float  # 0-10
    
    # Layer 6: Trade & Integration
    non_oil_exports_growth: float  # percentage
    caricom_integration_score: float  # 0-10
    export_diversification_index: float  # 0-1 (Herfindahl-Hirschman)
    
    # Layer 7: Climate & Resilience
    climate_budget_gdp_percent: float
    green_projects_count: int
    adaptation_funding_score: float  # 0-10
    
    # Layer 8: Digital Readiness
    ict_budget_percent: float
    egov_adoption_percent: float
    digital_literacy_score: float  # 0-10
    
    # Layer 9: Human Impact
    inflation_rate: float
    unemployment_rate: float
    real_wage_growth: float
    food_security_score: float  # 0-10


class BIICalculator:
    """
    Calculates Budget Intelligence Index using proprietary 9-Layer Framework
    """
    
    # Weights for each layer (must sum to 1.0)
    LAYER_WEIGHTS = {
        'fiscal_transparency': 0.12,
        'revenue_stability': 0.14,
        'debt_health': 0.15,
        'expenditure_efficiency': 0.13,
        'private_sector': 0.11,
        'trade_integration': 0.10,
        'climate_resilience': 0.08,
        'digital_readiness': 0.09,
        'human_impact': 0.08
    }
    
    @staticmethod
    def calculate_layer1_fiscal_transparency(
        budget_on_time: bool,
        audit_delay_years: int
    ) -> float:
        """
        Layer 1: Fiscal Transparency Score (0-10)
        
        Factors:
        - Budget published on time: +5 points
        - Audit delay: -1 point per year delayed (max -4)
        - Baseline: 5 points
        """
        score = 5.0  # baseline
        
        if budget_on_time:
            score += 5.0
        
        # Penalty for audit delays
        audit_penalty = min(audit_delay_years * 1.0, 4.0)
        score -= audit_penalty
        
        return max(0.0, min(10.0, score))
    
    @staticmethod
    def calculate_layer2_revenue_stability(
        non_oil_percent: float,
        tax_base_score: float,
        collection_efficiency: float
    ) -> float:
        """
        Layer 2: Revenue Stability Score (0-10)
        
        Formula: (non_oil% × 0.6) + (tax_base × 0.3) + (efficiency × 0.1)
        """
        score = (
            (non_oil_percent / 100 * 6.0) +
            (tax_base_score / 10 * 3.0) +
            (collection_efficiency / 10 * 1.0)
        ) * 10
        
        return max(0.0, min(10.0, score))
    
    @staticmethod
    def calculate_layer3_debt_health(
        debt_to_gdp: float,
        debt_service_to_revenue: float,
        fiscal_balance_trend: str
    ) -> float:
        """
        Layer 3: Public Debt Health Score (0-10)
        
        Grading:
        - Debt/GDP <60%: Excellent (8-10)
        - 60-75%: Good (6-8)
        - 75-85%: Moderate (4-6)
        - >85%: Poor (0-4)
        
        - Debt service <15%: Good (+1)
        - 15-20%: Moderate (0)
        - >20%: High (-1)
        
        - Fiscal trend: improving (+1), stable (0), declining (-1)
        """
        # Base score from debt/GDP
        if debt_to_gdp < 60:
            base_score = 9.0
        elif debt_to_gdp < 75:
            base_score = 7.0 - ((debt_to_gdp - 60) / 15 * 2)
        elif debt_to_gdp < 85:
            base_score = 5.0 - ((debt_to_gdp - 75) / 10 * 2)
        else:
            base_score = 2.0 - ((debt_to_gdp - 85) / 15 * 2)
        
        # Adjustment for debt service
        if debt_service_to_revenue < 15:
            base_score += 1.0
        elif debt_service_to_revenue > 20:
            base_score -= 1.0
        
        # Adjustment for trend
        trend_adjustment = {
            'improving': 1.0,
            'stable': 0.0,
            'declining': -1.0
        }.get(fiscal_balance_trend, 0.0)
        
        base_score += trend_adjustment
        
        return max(0.0, min(10.0, base_score))
    
    @staticmethod
    def calculate_layer4_expenditure_efficiency(
        productive_percent: float,
        consumption_percent: float
    ) -> float:
        """
        Layer 4: Expenditure Efficiency Score (0-10)
        
        Formula: (productive% / consumption%) × 5
        Benchmark: Productive should be ≥50% of consumption
        """
        if consumption_percent == 0:
            return 0.0
        
        ratio = productive_percent / consumption_percent
        score = ratio * 5.0
        
        return max(0.0, min(10.0, score))
    
    @staticmethod
    def calculate_layer5_private_sector(
        ease_of_business_rank: int,
        sme_delivery_rate: float,
        forex_access: float
    ) -> float:
        """
        Layer 5: Private Sector Climate Score (0-10)
        
        Components:
        - Ease of business (0-4 points): Top 50 = 4, 51-100 = 3, 101-150 = 2, >150 = 1
        - SME support delivery (0-4 points): delivery_rate / 25
        - Forex access (0-2 points): forex_score / 5
        """
        # Ease of business score
        if ease_of_business_rank <= 50:
            eob_score = 4.0
        elif ease_of_business_rank <= 100:
            eob_score = 3.0
        elif ease_of_business_rank <= 150:
            eob_score = 2.0
        else:
            eob_score = 1.0
        
        # SME delivery score
        sme_score = min(sme_delivery_rate / 25, 4.0)
        
        # Forex access score
        forex_score = min(forex_access / 5, 2.0)
        
        total_score = eob_score + sme_score + forex_score
        
        return max(0.0, min(10.0, total_score))
    
    @staticmethod
    def calculate_layer6_trade_integration(
        export_growth: float,
        caricom_integration: float,
        diversification_index: float
    ) -> float:
        """
        Layer 6: Trade & Integration Score (0-10)
        
        Components:
        - Export growth (0-4 points): +5% = 2, +10% = 4, <0% = 0
        - CARICOM integration (0-3 points): integration_score / 3.33
        - Diversification (0-3 points): (1 - HHI) × 3
        """
        # Export growth score
        if export_growth >= 10:
            growth_score = 4.0
        elif export_growth >= 5:
            growth_score = 2.0 + (export_growth - 5) / 5 * 2
        elif export_growth >= 0:
            growth_score = export_growth / 5 * 2
        else:
            growth_score = 0.0
        
        # CARICOM score
        caricom_score = min(caricom_integration / 3.33, 3.0)
        
        # Diversification score (lower HHI = better)
        div_score = (1 - diversification_index) * 3.0
        
        total_score = growth_score + caricom_score + div_score
        
        return max(0.0, min(10.0, total_score))
    
    @staticmethod
    def calculate_layer7_climate_resilience(
        climate_budget_gdp: float,
        projects_count: int,
        adaptation_funding: float
    ) -> float:
        """
        Layer 7: Climate & Resilience Score (0-10)
        
        Components:
        - Climate budget % GDP (0-4 points): 2% = 4, 1% = 2, <0.5% = 1
        - Projects count (0-3 points): 10+ = 3, 5-9 = 2, 1-4 = 1
        - Adaptation funding (0-3 points): funding_score / 3.33
        """
        # Budget allocation score
        if climate_budget_gdp >= 2.0:
            budget_score = 4.0
        elif climate_budget_gdp >= 1.0:
            budget_score = 2.0 + (climate_budget_gdp - 1.0) * 2
        elif climate_budget_gdp >= 0.5:
            budget_score = 1.0 + (climate_budget_gdp - 0.5) * 2
        else:
            budget_score = climate_budget_gdp / 0.5
        
        # Projects score
        if projects_count >= 10:
            projects_score = 3.0
        elif projects_count >= 5:
            projects_score = 2.0
        elif projects_count >= 1:
            projects_score = 1.0
        else:
            projects_score = 0.0
        
        # Adaptation funding score
        adaptation_score = min(adaptation_funding / 3.33, 3.0)
        
        total_score = budget_score + projects_score + adaptation_score
        
        return max(0.0, min(10.0, total_score))
    
    @staticmethod
    def calculate_layer8_digital_readiness(
        ict_budget_percent: float,
        egov_adoption: float,
        digital_literacy: float
    ) -> float:
        """
        Layer 8: Digital Readiness Score (0-10)
        
        Components:
        - ICT budget % (0-3 points): 2% = 3, 1% = 2, <0.5% = 1
        - E-gov adoption (0-4 points): 50% = 4, 25% = 2
        - Digital literacy (0-3 points): literacy_score / 3.33
        """
        # ICT budget score
        if ict_budget_percent >= 2.0:
            ict_score = 3.0
        elif ict_budget_percent >= 1.0:
            ict_score = 2.0 + (ict_budget_percent - 1.0)
        elif ict_budget_percent >= 0.5:
            ict_score = 1.0 + (ict_budget_percent - 0.5) * 2
        else:
            ict_score = ict_budget_percent / 0.5
        
        # E-gov adoption score
        if egov_adoption >= 50:
            egov_score = 4.0
        elif egov_adoption >= 25:
            egov_score = 2.0 + (egov_adoption - 25) / 25 * 2
        else:
            egov_score = egov_adoption / 25 * 2
        
        # Digital literacy score
        literacy_score = min(digital_literacy / 3.33, 3.0)
        
        total_score = ict_score + egov_score + literacy_score
        
        return max(0.0, min(10.0, total_score))
    
    @staticmethod
    def calculate_layer9_human_impact(
        inflation: float,
        unemployment: float,
        real_wage_growth: float,
        food_security: float
    ) -> float:
        """
        Layer 9: Human Impact Score (0-10)
        
        Components:
        - Inflation (0-3 points): <2% = 3, 2-4% = 2, 4-6% = 1, >6% = 0
        - Unemployment (0-3 points): <4% = 3, 4-6% = 2, 6-8% = 1, >8% = 0
        - Real wage growth (0-2 points): >2% = 2, 0-2% = 1, <0% = 0
        - Food security (0-2 points): food_score / 5
        """
        # Inflation score
        if inflation < 2:
            inflation_score = 3.0
        elif inflation < 4:
            inflation_score = 2.0
        elif inflation < 6:
            inflation_score = 1.0
        else:
            inflation_score = 0.0
        
        # Unemployment score
        if unemployment < 4:
            unemp_score = 3.0
        elif unemployment < 6:
            unemp_score = 2.0
        elif unemployment < 8:
            unemp_score = 1.0
        else:
            unemp_score = 0.0
        
        # Wage growth score
        if real_wage_growth > 2:
            wage_score = 2.0
        elif real_wage_growth > 0:
            wage_score = 1.0
        else:
            wage_score = 0.0
        
        # Food security score
        food_score = min(food_security / 5, 2.0)
        
        total_score = inflation_score + unemp_score + wage_score + food_score
        
        return max(0.0, min(10.0, total_score))
    
    @classmethod
    def calculate_bii(cls, inputs: LayerInputs) -> Dict[str, float]:
        """
        Calculate complete BII score from all 9 layers
        
        Returns:
            Dictionary with all layer scores + overall BII + grade
        """
        # Calculate each layer
        layer1 = cls.calculate_layer1_fiscal_transparency(
            inputs.budget_on_time,
            inputs.audit_delay_years
        )
        
        layer2 = cls.calculate_layer2_revenue_stability(
            inputs.non_oil_revenue_percent,
            inputs.tax_base_breadth_score,
            inputs.collection_efficiency
        )
        
        layer3 = cls.calculate_layer3_debt_health(
            inputs.debt_to_gdp,
            inputs.debt_service_to_revenue,
            inputs.fiscal_balance_trend
        )
        
        layer4 = cls.calculate_layer4_expenditure_efficiency(
            inputs.productive_spending_percent,
            inputs.consumption_spending_percent
        )
        
        layer5 = cls.calculate_layer5_private_sector(
            inputs.ease_of_business_rank,
            inputs.sme_support_delivery_rate,
            inputs.forex_access_score
        )
        
        layer6 = cls.calculate_layer6_trade_integration(
            inputs.non_oil_exports_growth,
            inputs.caricom_integration_score,
            inputs.export_diversification_index
        )
        
        layer7 = cls.calculate_layer7_climate_resilience(
            inputs.climate_budget_gdp_percent,
            inputs.green_projects_count,
            inputs.adaptation_funding_score
        )
        
        layer8 = cls.calculate_layer8_digital_readiness(
            inputs.ict_budget_percent,
            inputs.egov_adoption_percent,
            inputs.digital_literacy_score
        )
        
        layer9 = cls.calculate_layer9_human_impact(
            inputs.inflation_rate,
            inputs.unemployment_rate,
            inputs.real_wage_growth,
            inputs.food_security_score
        )
        
        # Calculate weighted overall BII
        bii_overall = (
            layer1 * cls.LAYER_WEIGHTS['fiscal_transparency'] +
            layer2 * cls.LAYER_WEIGHTS['revenue_stability'] +
            layer3 * cls.LAYER_WEIGHTS['debt_health'] +
            layer4 * cls.LAYER_WEIGHTS['expenditure_efficiency'] +
            layer5 * cls.LAYER_WEIGHTS['private_sector'] +
            layer6 * cls.LAYER_WEIGHTS['trade_integration'] +
            layer7 * cls.LAYER_WEIGHTS['climate_resilience'] +
            layer8 * cls.LAYER_WEIGHTS['digital_readiness'] +
            layer9 * cls.LAYER_WEIGHTS['human_impact']
        )
        
        # Assign grade
        grade = cls._calculate_grade(bii_overall)
        
        return {
            'layer1_fiscal_transparency': round(layer1, 1),
            'layer2_revenue_stability': round(layer2, 1),
            'layer3_debt_health': round(layer3, 1),
            'layer4_expenditure_efficiency': round(layer4, 1),
            'layer5_private_sector': round(layer5, 1),
            'layer6_trade_integration': round(layer6, 1),
            'layer7_climate_resilience': round(layer7, 1),
            'layer8_digital_readiness': round(layer8, 1),
            'layer9_human_impact': round(layer9, 1),
            'bii_overall': round(bii_overall, 1),
            'bii_grade': grade
        }
    
    @staticmethod
    def _calculate_grade(score: float) -> str:
        """Convert BII score to letter grade"""
        if score >= 9.5:
            return 'A+'
        elif score >= 9.0:
            return 'A'
        elif score >= 8.5:
            return 'A-'
        elif score >= 8.0:
            return 'B+'
        elif score >= 7.0:
            return 'B'
        elif score >= 6.5:
            return 'B-'
        elif score >= 6.0:
            return 'C+'
        elif score >= 5.0:
            return 'C'
        elif score >= 4.5:
            return 'C-'
        elif score >= 4.0:
            return 'D+'
        elif score >= 3.0:
            return 'D'
        elif score >= 2.0:
            return 'D-'
        else:
            return 'F'


# ============================================================================
# EXAMPLE USAGE: Trinidad & Tobago FY 2026
# ============================================================================

if __name__ == "__main__":
    # Sample data for T&T 2026
    inputs_2026 = LayerInputs(
        # Layer 1
        budget_on_time=True,
        audit_delay_years=2,
        
        # Layer 2
        non_oil_revenue_percent=78.0,
        tax_base_breadth_score=5.0,
        collection_efficiency=5.0,
        
        # Layer 3
        debt_to_gdp=81.8,
        debt_service_to_revenue=20.6,
        fiscal_balance_trend="declining",
        
        # Layer 4
        productive_spending_percent=25.4,
        consumption_spending_percent=50.3,
        
        # Layer 5
        ease_of_business_rank=105,
        sme_support_delivery_rate=28.0,
        forex_access_score=4.0,
        
        # Layer 6
        non_oil_exports_growth=-6.0,
        caricom_integration_score=5.2,
        export_diversification_index=0.78,  # High = concentrated
        
        # Layer 7
        climate_budget_gdp_percent=0.18,
        green_projects_count=5,
        adaptation_funding_score=3.6,
        
        # Layer 8
        ict_budget_percent=0.9,
        egov_adoption_percent=32.0,
        digital_literacy_score=5.1,
        
        # Layer 9
        inflation_rate=0.3,
        unemployment_rate=4.2,
        real_wage_growth=-0.5,
        food_security_score=5.4
    )
    
    calculator = BIICalculator()
    results = calculator.calculate_bii(inputs_2026)
    
    print("=" * 60)
    print("CARIBBEAN BUDGET INTELLIGENCE™ - BII CALCULATION")
    print("=" * 60)
    print(f"Country: Trinidad & Tobago")
    print(f"Fiscal Year: 2026")
    print("=" * 60)
    print(f"\n📊 LAYER SCORES:")
    print(f"  1️⃣  Fiscal Transparency:      {results['layer1_fiscal_transparency']}/10")
    print(f"  2️⃣  Revenue Stability:        {results['layer2_revenue_stability']}/10")
    print(f"  3️⃣  Public Debt Health:       {results['layer3_debt_health']}/10")
    print(f"  4️⃣  Expenditure Efficiency:   {results['layer4_expenditure_efficiency']}/10")
    print(f"  5️⃣  Private Sector Climate:   {results['layer5_private_sector']}/10")
    print(f"  6️⃣  Trade & Integration:      {results['layer6_trade_integration']}/10")
    print(f"  7️⃣  Climate & Resilience:     {results['layer7_climate_resilience']}/10")
    print(f"  8️⃣  Digital Readiness:        {results['layer8_digital_readiness']}/10")
    print(f"  9️⃣  Human Impact:             {results['layer9_human_impact']}/10")
    print("=" * 60)
    print(f"\n🎯 OVERALL BII SCORE: {results['bii_overall']}/10")
    print(f"📝 GRADE: {results['bii_grade']}")
    print("=" * 60)
