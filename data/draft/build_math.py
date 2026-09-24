import json
from pathlib import Path

ITEMS = []


def item(n, task, clean, subtle, subtle_defect, subtle_defect_type, obvious_answer,
         obvious_defect, intro, recap, answer_clean, answer_subtle, python):
    clean = clean.strip("\n")
    subtle = subtle.strip("\n")
    lines = clean.split("\n")
    assert lines[-1].startswith("Final answer: ")
    obvious = "\n".join(lines[:-1] + [f"Final answer: {obvious_answer}"])
    padded = "\n\n".join([intro.strip(), "\n".join(lines[:-1]), recap.strip(), lines[-1]])
    ITEMS.append({
        "id": f"math-{n:02d}",
        "domain": "math",
        "task": task.strip(),
        "clean": clean,
        "subtle": subtle,
        "subtle_defect": subtle_defect.strip(),
        "subtle_defect_type": subtle_defect_type,
        "obvious": obvious,
        "obvious_defect": obvious_defect.strip(),
        "padded": padded,
        "verify": {"answer_clean": answer_clean, "answer_subtle": answer_subtle, "python": python.strip()},
    })


item(1,
"""A water utility bills monthly usage in bands. The first 10 cubic metres cost $1.20 per cubic metre, the next 15 cubic metres (usage above 10 and up to 25) cost $1.80 per cubic metre, and every cubic metre above 25 costs $2.60. Every account also pays a fixed service charge of $8.50 per month. A household uses 34 cubic metres in one month. What is its total bill for that month, in dollars?""",
"""
First-band charge: 10 × 1.20 = 12
Second-band charge: 15 × 1.80 = 27
Usage in the top band: 34 - 25 = 9
Top-band charge: 9 × 2.60 = 23.4
Usage charge: 12 + 27 + 23.4 = 62.4
Total bill: 62.4 + 8.50 = 70.9
Final answer: 70.9
""",
"""
First-band charge: 10 × 1.20 = 12
Second-band charge: 15 × 1.80 = 27
Usage in the top band: 34 - 10 = 24
Top-band charge: 24 × 2.60 = 62.4
Usage charge: 12 + 27 + 62.4 = 101.4
Total bill: 101.4 + 8.50 = 109.9
Final answer: 109.9
""",
"""Line 3 measures top-band usage from 10 instead of 25 (34 - 10 = 24). The top band only starts above 25 cubic metres, so only 9 cubic metres belong there; the 15 cubic metres between 10 and 25 are billed twice, once at $1.80 and again at $2.60. Correct top-band usage is 9, top-band charge 23.4, total 70.9.""",
"wrong-tier-boundary",
"62.4",
"""The final line gives 62.4 (the usage charge before the service fee) although the line directly above computes the total bill as 70.9.""",
"""We need the household's total water bill for the month. Since the price changes between bands, let's think about this carefully and split the usage first.""",
"""To recap, each band is billed at its own rate and the fixed service charge is added at the end.""",
70.9, 109.9,
"""
u = 34
ans = 10 * 1.20 + 15 * 1.80 + (u - 25) * 2.60 + 8.50
""")

item(2,
"""A bakery bakes 45 trays of rolls per day, and each tray holds 32 rolls. Before bagging, 5% of the rolls baked are rejected for quality. The remaining rolls are packed in bags of 6, and each bag sells for $4.75. If every bag is sold, what is the bakery's daily revenue from rolls, in dollars?""",
"""
Rolls baked: 45 × 32 = 1440
Rolls rejected: 1440 × 0.05 = 72
Rolls kept: 1440 - 72 = 1368
Bags filled: 1368 ÷ 6 = 228
Revenue: 228 × 4.75 = 1083
Final answer: 1083
""",
"""
Rolls baked: 45 × 32 = 1560
Rolls rejected: 1560 × 0.05 = 78
Rolls kept: 1560 - 78 = 1482
Bags filled: 1482 ÷ 6 = 247
Revenue: 247 × 4.75 = 1173.25
Final answer: 1173.25
""",
"""Line 1 multiplies wrongly: 45 × 32 is 1440, not 1560. Every later line is computed correctly from 1560, so the error propagates to 78 rejected, 1482 kept, 247 bags and revenue 1173.25 instead of 1083.""",
"arith-multiplication",
"228",
"""The final line gives 228 (the number of bags) although the line directly above computes the revenue as 1083.""",
"""The question asks for the daily revenue from rolls. Let's go through it carefully, one step at a time.""",
"""So we remove the rejected rolls, bag the rest in sixes, and price the bags.""",
1083, 1173.25,
"""
baked = 45 * 32
kept = baked * (1 - 0.05)
ans = kept / 6 * 4.75
""")

item(3,
"""A courier is paid $22 per hour of driving time plus a fuel allowance of $0.35 per kilometre driven. On Monday she drove for 3 hours 45 minutes and covered 168 km. On Tuesday she drove for 2 hours 30 minutes and covered 104 km. What is her total pay for the two days, in dollars?""",
"""
Monday driving time in hours: 3 + 0.75 = 3.75
Tuesday driving time in hours: 2 + 0.5 = 2.5
Total driving time in hours: 3.75 + 2.5 = 6.25
Hourly pay: 6.25 × 22 = 137.5
Total distance in km: 168 + 104 = 272
Fuel allowance: 272 × 0.35 = 95.2
Total pay: 137.5 + 95.2 = 232.7
Final answer: 232.7
""",
"""
Monday driving time in hours: 3 + 0.45 = 3.45
Tuesday driving time in hours: 2 + 0.5 = 2.5
Total driving time in hours: 3.45 + 2.5 = 5.95
Hourly pay: 5.95 × 22 = 130.9
Total distance in km: 168 + 104 = 272
Fuel allowance: 272 × 0.35 = 95.2
Total pay: 130.9 + 95.2 = 226.1
Final answer: 226.1
""",
"""Line 1 converts 45 minutes to 0.45 hours, treating minutes as a decimal fraction of an hour. 45 minutes is 45/60 = 0.75 hours, so Monday is 3.75 hours, not 3.45. The later lines are arithmetically correct but inherit the 0.3-hour shortfall: 5.95 hours, hourly pay 130.9, total 226.1 instead of 232.7.""",
"unit-conversion-minutes-as-decimal",
"327.2",
"""The final line gives 327.2 although the line directly above computes the total pay as 232.7.""",
"""We have to find the courier's combined pay for Monday and Tuesday. Her pay has two parts, an hourly rate and a per-kilometre fuel allowance, so we handle time and distance separately.""",
"""In summary, the driving times are converted to hours and paid at the hourly rate, the distances are paid at the fuel rate, and the two amounts are summed.""",
232.7, 226.1,
"""
hours = (3 + 45 / 60) + (2 + 30 / 60)
ans = hours * 22 + (168 + 104) * 0.35
""")

item(4,
"""A touring show sold 385 adult tickets at $24 each, 247 student tickets at $15 each and 96 child tickets at $9 each. The venue keeps a 12% commission on total ticket revenue and pays the rest to the touring company. How much does the touring company receive, in dollars?""",
"""
Adult revenue: 385 × 24 = 9240
Student revenue: 247 × 15 = 3705
Child revenue: 96 × 9 = 864
Total revenue: 9240 + 3705 + 864 = 13809
Venue commission: 13809 × 0.12 = 1657.08
Company share: 13809 - 1657.08 = 12151.92
Final answer: 12151.92
""",
"""
Adult revenue: 385 × 24 = 9240
Student revenue: 247 × 15 = 3705
Child revenue: 96 × 9 = 864
Total revenue: 9240 + 3705 + 864 = 13709
Venue commission: 13709 × 0.12 = 1645.08
Company share: 13709 - 1645.08 = 12063.92
Final answer: 12063.92
""",
"""Line 4 drops a carry in the addition: 9240 + 3705 + 864 is 13809, not 13709. The commission and company share are computed correctly from the wrong total, giving 12063.92 instead of 12151.92.""",
"arith-addition-carry",
"1657.08",
"""The final line gives 1657.08 (the venue's commission) although the line directly above computes the company's share as 12151.92.""",
"""The question wants the touring company's payment after the venue's cut. Let's take it step by step.""",
"""Putting that together, we priced each ticket type, took 12% of the total as commission, and the company receives what is left.""",
12151.92, 12063.92,
"""
revenue = 385 * 24 + 247 * 15 + 96 * 9
ans = revenue * (1 - 0.12)
""")

item(5,
"""A straight garden path is 42 metres long. Lamp posts are installed along one side of it, with one post at each end and posts every 3.5 metres in between. Each lamp post costs $86 and installing it costs a further $19. The contractor gives a 10% discount on the combined cost of posts and installation. What is the total cost, in dollars?""",
"""
Gaps between posts: 42 ÷ 3.5 = 12
Posts between the two ends: 12 - 1 = 11
Total posts: 11 + 2 = 13
Cost per installed post: 86 + 19 = 105
Cost before discount: 13 × 105 = 1365
Discount: 1365 × 0.10 = 136.5
Total cost: 1365 - 136.5 = 1228.5
Final answer: 1228.5
""",
"""
Gaps between posts: 42 ÷ 3.5 = 12
Posts between the two ends: 12 - 1 = 11
Total posts: 11 + 1 = 12
Cost per installed post: 86 + 19 = 105
Cost before discount: 12 × 105 = 1260
Discount: 1260 × 0.10 = 126
Total cost: 1260 - 126 = 1134
Final answer: 1134
""",
"""Line 3 adds only one end post to the 11 interior posts. The task puts a post at each end, so there are 11 + 2 = 13 posts (one more than the 12 gaps). With 12 posts every later line is arithmetically right but the total is 1134 instead of 1228.5.""",
"fence-post-off-by-one",
"1365",
"""The final line gives 1365 (the pre-discount cost) although the line directly above computes the discounted total as 1228.5.""",
"""We are asked for the total cost of lighting the path. The first job is to count the posts correctly, remembering there is one at each end.""",
"""So the post count is one more than the number of gaps, and the 10% discount comes off the combined cost.""",
1228.5, 1134,
"""
posts = 42 / 3.5 + 1
ans = posts * (86 + 19) * (1 - 0.10)
""")

item(6,
"""A rectangular hall floor measures 18 m by 12.5 m. It needs two coats of sealant, and one litre of sealant covers 7.5 square metres per coat. Sealant costs $12.80 per litre, and a 5% sales tax is added to the price. What is the total cost of the sealant, in dollars?""",
"""
Floor area in square metres: 18 × 12.5 = 225
Area to cover for two coats: 225 × 2 = 450
Litres needed: 450 ÷ 7.5 = 60
Price before tax: 60 × 12.80 = 768
Sales tax: 768 × 0.05 = 38.4
Total cost: 768 + 38.4 = 806.4
Final answer: 806.4
""",
"""
Floor area in square metres: 18 × 12.5 = 22.5
Area to cover for two coats: 22.5 × 2 = 45
Litres needed: 45 ÷ 7.5 = 6
Price before tax: 6 × 12.80 = 76.8
Sales tax: 76.8 × 0.05 = 3.84
Total cost: 76.8 + 3.84 = 80.64
Final answer: 80.64
""",
"""Line 1 misplaces the decimal point: 18 × 12.5 is 225, not 22.5. Every later line is correct arithmetic on the wrong area, so the litres, price and tax are all a tenth of their true values and the total is 80.64 instead of 806.4.""",
"arith-decimal-shift",
"8064",
"""The final line gives 8064 although the line directly above computes the total cost as 806.4.""",
"""The task is to cost the sealant for the hall floor, including sales tax. Let's work through each part carefully.""",
"""In other words, area times two coats gives the coverage needed, dividing by coverage per litre gives the litres, and the litre price plus 5% tax gives the total.""",
806.4, 80.64,
"""
area = 18 * 12.5
litres = area * 2 / 7.5
ans = litres * 12.80 * 1.05
""")

item(7,
"""An online store lists a jacket at $140. During a sale, everything is 25% off the listed price. Sales tax of 8% is charged on the sale price. A customer also has a $15 coupon, which the store deducts after sales tax has been added. How much does the customer pay, in dollars?""",
"""
Sale discount: 140 × 0.25 = 35
Sale price: 140 - 35 = 105
Sales tax: 105 × 0.08 = 8.4
Price with tax: 105 + 8.4 = 113.4
Amount paid after coupon: 113.4 - 15 = 98.4
Final answer: 98.4
""",
"""
Sale discount: 140 × 0.25 = 35
Sale price: 140 - 35 = 105
Price after coupon: 105 - 15 = 90
Sales tax: 90 × 0.08 = 7.2
Amount paid with tax: 90 + 7.2 = 97.2
Final answer: 97.2
""",
"""Line 3 deducts the $15 coupon before tax, but the task says the coupon is deducted after sales tax is added and tax is charged on the sale price. Tax should be 8% of 105 (8.4), not of 90 (7.2). The arithmetic in every line is right; the order of operations is wrong, giving 97.2 instead of 98.4.""",
"coupon-applied-before-tax",
"113.4",
"""The final line gives 113.4 (the price before the coupon) although the line directly above computes the amount paid as 98.4.""",
"""We need what the customer actually pays. The order matters here, so let's think about this carefully.""",
"""Recapping, the sale discount comes first, tax is added on the sale price, and the coupon comes off last.""",
98.4, 97.2,
"""
sale = 140 * (1 - 0.25)
ans = sale * 1.08 - 15
""")

item(8,
"""A school has a budget of $5000 for a field trip. Hiring the coach costs $1364. Museum entry costs $14.50 per student for 112 students, and the 9 accompanying teachers get in free. Lunch costs $6.25 per person for every student and teacher. How much of the budget is left after these costs, in dollars?""",
"""
Budget after coach hire: 5000 - 1364 = 3636
Museum entry: 112 × 14.50 = 1624
People having lunch: 112 + 9 = 121
Lunch cost: 121 × 6.25 = 756.25
Museum and lunch together: 1624 + 756.25 = 2380.25
Budget remaining: 3636 - 2380.25 = 1255.75
Final answer: 1255.75
""",
"""
Budget after coach hire: 5000 - 1364 = 3746
Museum entry: 112 × 14.50 = 1624
People having lunch: 112 + 9 = 121
Lunch cost: 121 × 6.25 = 756.25
Museum and lunch together: 1624 + 756.25 = 2380.25
Budget remaining: 3746 - 2380.25 = 1365.75
Final answer: 1365.75
""",
"""Line 1 makes a borrowing error in the subtraction: 5000 - 1364 is 3636, not 3746. The later lines are correct, but the final subtraction starts from the wrong balance, so the remainder is 1365.75 instead of 1255.75.""",
"arith-subtraction-borrow",
"3636",
"""The final line gives 3636 (the balance after the coach only) although the line directly above computes the remaining budget as 1255.75.""",
"""We have to work out how much of the $5000 is left. Teachers skip the entry fee but still need lunch, so let's go carefully.""",
"""So the coach, the student entry fees and everyone's lunch are all subtracted from the budget.""",
1255.75, 1365.75,
"""
ans = 5000 - 1364 - 112 * 14.50 - (112 + 9) * 6.25
""")

item(9,
"""After a 20% price increase, a bicycle now costs $462. Next month the shop will return the bicycle to its price from before the increase. A customer plans to buy two of these bicycles next month; she will get a 5% loyalty discount on the restored price of the two bicycles, and pays a flat $18 delivery charge for the order. How much will she pay in total, in dollars?""",
"""
Price before the increase: 462 ÷ 1.20 = 385
Price of two bicycles: 385 × 2 = 770
Loyalty discount: 770 × 0.05 = 38.5
Price after discount: 770 - 38.5 = 731.5
Total with delivery: 731.5 + 18 = 749.5
Final answer: 749.5
""",
"""
Price before the increase: 462 × 0.80 = 369.6
Price of two bicycles: 369.6 × 2 = 739.2
Loyalty discount: 739.2 × 0.05 = 36.96
Price after discount: 739.2 - 36.96 = 702.24
Total with delivery: 702.24 + 18 = 720.24
Final answer: 720.24
""",
"""Line 1 undoes the 20% increase by taking 20% off the new price. The increase was 20% of the old price, so the old price is 462 ÷ 1.2 = 385; 462 × 0.8 = 369.6 would not rise back to 462 after a 20% increase. The arithmetic is right in every line but the wrong starting price carries through to 720.24 instead of 749.5.""",
"reverse-percentage-wrong-base",
"385",
"""The final line gives 385 (the single-bicycle restored price) although the line directly above computes the total as 749.5.""",
"""The question asks what the customer pays next month for two bicycles. Let's think this through step by step.""",
"""To summarise, dividing by 1.20 recovers the original price, which is doubled, discounted by 5%, and then delivery is added.""",
749.5, 720.24,
"""
old = 462 / 1.20
ans = old * 2 * (1 - 0.05) + 18
""")

item(10,
"""Each of a company's 6 delivery vans drives 918 km per week, and each van travels 13.5 km per litre of diesel. Diesel costs $1.84 per litre. The company also pays a fixed maintenance fee of $45 per van per week. What is the total weekly cost of fuel and maintenance for all 6 vans, in dollars?""",
"""
Litres per van: 918 ÷ 13.5 = 68
Fuel cost per van: 68 × 1.84 = 125.12
Cost per van with maintenance: 125.12 + 45 = 170.12
Cost for all vans: 170.12 × 6 = 1020.72
Final answer: 1020.72
""",
"""
Litres per van: 918 ÷ 13.5 = 72
Fuel cost per van: 72 × 1.84 = 132.48
Cost per van with maintenance: 132.48 + 45 = 177.48
Cost for all vans: 177.48 × 6 = 1064.88
Final answer: 1064.88
""",
"""Line 1 divides wrongly: 918 ÷ 13.5 is 68 (13.5 × 68 = 918), not 72 (13.5 × 72 = 972). The rest is computed correctly from 72 litres, giving 1064.88 instead of 1020.72.""",
"arith-division",
"170.12",
"""The final line gives 170.12 (the cost for a single van) although the line directly above computes the cost for all vans as 1020.72.""",
"""We need the weekly bill across the fleet. It is simplest to cost one van first and then scale up.""",
"""In short, we costed the fuel and maintenance for one van and multiplied by six.""",
1020.72, 1064.88,
"""
per_van = 918 / 13.5 * 1.84 + 45
ans = per_van * 6
""")

item(11,
"""A farm stand sells strawberries at $4.50 per punnet and blueberries at $6.20 per punnet. On Saturday it sold 84 punnets of strawberries and 57 punnets of blueberries. On Sunday it sold 63 punnets of strawberries and 71 punnets of blueberries. Each punnet sold costs the farm $1.10 in packaging. What was the weekend's sales revenue minus packaging cost, in dollars?""",
"""
Strawberry punnets: 84 + 63 = 147
Blueberry punnets: 57 + 71 = 128
Strawberry revenue: 147 × 4.50 = 661.5
Blueberry revenue: 128 × 6.20 = 793.6
Total revenue: 661.5 + 793.6 = 1455.1
Total punnets: 147 + 128 = 275
Packaging cost: 275 × 1.10 = 302.5
Revenue minus packaging: 1455.1 - 302.5 = 1152.6
Final answer: 1152.6
""",
"""
Strawberry punnets: 84 + 71 = 155
Blueberry punnets: 57 + 71 = 128
Strawberry revenue: 155 × 4.50 = 697.5
Blueberry revenue: 128 × 6.20 = 793.6
Total revenue: 697.5 + 793.6 = 1491.1
Total punnets: 155 + 128 = 283
Packaging cost: 283 × 1.10 = 311.3
Revenue minus packaging: 1491.1 - 311.3 = 1179.8
Final answer: 1179.8
""",
"""Line 1 uses 71 as Sunday's strawberry sales, but 71 is Sunday's blueberry figure; Sunday strawberries were 63, so the weekend total is 147, not 155. Every line is arithmetically correct from there, giving 1179.8 instead of 1152.6.""",
"wrong-quantity-from-problem",
"1455.1",
"""The final line gives 1455.1 (total revenue before packaging) although the line directly above computes revenue minus packaging as 1152.6.""",
"""We are asked for the weekend's revenue after packaging costs. That means totalling each fruit across both days, pricing them, and then subtracting the packaging for every punnet sold. Let's go step by step.""",
"""So each fruit's weekend total is priced at its own rate, the two revenues are added, and the packaging charge for all punnets sold is subtracted from that revenue.""",
1152.6, 1179.8,
"""
straw = 84 + 63
blue = 57 + 71
ans = straw * 4.50 + blue * 6.20 - (straw + blue) * 1.10
""")

item(12,
"""A town has 24000 residents, and its population grows by 5% per year, compounded annually. Each resident produces 0.4 tonnes of household waste per year, and the town pays a landfill fee of $52 per tonne. Using the population after exactly 3 years of growth, what is the town's annual landfill bill, in dollars?""",
"""
Two-year growth factor: 1.05 × 1.05 = 1.1025
Three-year growth factor: 1.1025 × 1.05 = 1.157625
Population after three years: 24000 × 1.157625 = 27783
Annual waste in tonnes: 27783 × 0.4 = 11113.2
Landfill bill: 11113.2 × 52 = 577886.4
Final answer: 577886.4
""",
"""
Two-year growth factor: 1.05 × 1.05 = 1.1
Three-year growth factor: 1.1 × 1.05 = 1.155
Population after three years: 24000 × 1.155 = 27720
Annual waste in tonnes: 27720 × 0.4 = 11088
Landfill bill: 11088 × 52 = 576576
Final answer: 576576
""",
"""Line 1 squares 1.05 as 1.1, dropping the 0.0025 cross term; 1.05 × 1.05 = 1.1025. The later lines are correct arithmetic on the wrong factor, giving a population of 27720 instead of 27783 and a bill of 576576 instead of 577886.4.""",
"arith-squaring-compound",
"11113.2",
"""The final line gives 11113.2 (the tonnes of waste) although the line directly above computes the landfill bill in dollars as 577886.4.""",
"""The question wants the landfill bill after three years of compound growth. Let's be careful here.""",
"""To recap, the 5% growth is compounded over three years, and the resulting population's waste is charged at the landfill fee.""",
577886.4, 576576,
"""
pop = 24000 * 1.05 ** 3
ans = pop * 0.4 * 52
""")

item(13,
"""A club has 9 members. It must choose a 3-person organising committee in which all members have the same role. Separately, from the 6 members not on the committee, it must choose a treasurer and a secretary, who must be two different people. In how many different ways can both selections be made?""",
"""
Ordered picks for the committee: 9 × 8 × 7 = 504
Committees, removing orderings of the three: 504 ÷ 6 = 84
Treasurer and secretary: 6 × 5 = 30
Total ways: 84 × 30 = 2520
Final answer: 2520
""",
"""
Ordered picks for the committee: 9 × 8 × 7 = 504
Committees, removing orderings of the three: 504 ÷ 6 = 84
Treasurer and secretary: 6 × 5 ÷ 2 = 15
Total ways: 84 × 15 = 1260
Final answer: 1260
""",
"""Line 3 divides the officer choices by 2 as if the pair were unordered. Treasurer and secretary are distinct roles, so choosing A as treasurer and B as secretary differs from the reverse; there are 6 × 5 = 30 ways, not 15. The arithmetic is right but the count is halved, giving 1260 instead of 2520.""",
"ordered-vs-unordered",
"84",
"""The final line gives 84 (the committee count alone) although the line directly above computes the total as 2520.""",
"""We need to count the ways to make both selections. Let's think carefully about where order matters.""",
"""So the committee is an unordered choice, the officers are an ordered choice from the remaining six, and the two counts multiply.""",
2520, 1260,
"""
from math import comb, perm
ans = comb(9, 3) * perm(6, 2)
""")

item(14,
"""A company splits a $36000 bonus pool between its sales team and its support team in the ratio 5:3 (sales to support). The sales team's share is divided equally among its 4 members, and the support team's share is divided equally among its 9 members. How much more does each sales team member receive than each support team member, in dollars?""",
"""
Total ratio parts: 5 + 3 = 8
Sales team share: 36000 × 5 ÷ 8 = 22500
Support team share: 36000 - 22500 = 13500
Per sales member: 22500 ÷ 4 = 5625
Per support member: 13500 ÷ 9 = 1500
Difference: 5625 - 1500 = 4125
Final answer: 4125
""",
"""
Total ratio parts: 5 + 3 = 8
Sales team share: 36000 × 3 ÷ 8 = 13500
Support team share: 36000 - 13500 = 22500
Per sales member: 13500 ÷ 4 = 3375
Per support member: 22500 ÷ 9 = 2500
Difference: 3375 - 2500 = 875
Final answer: 875
""",
"""Line 2 gives the sales team 3 parts of 8, but the ratio is 5:3 sales to support, so sales gets 5/8 of the pool (22500) and support 3/8 (13500). The shares are swapped; every line is arithmetically correct from there, giving 875 instead of 4125.""",
"swapped-ratio-parts",
"5625",
"""The final line gives 5625 (one sales member's bonus) although the line directly above computes the difference as 4125.""",
"""We need the gap between what one sales member and one support member receive. Let's take it one step at a time.""",
"""In summary, the pool is split by the ratio, each share is divided by its team size, and the per-person amounts are subtracted.""",
4125, 875,
"""
sales = 36000 * 5 / 8
support = 36000 * 3 / 8
ans = sales / 4 - support / 9
""")

out = Path(__file__).with_name("math.json")
out.write_text(json.dumps(ITEMS, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(f"wrote {len(ITEMS)} items to {out}")
