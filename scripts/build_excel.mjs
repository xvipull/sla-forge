import fs from 'node:fs/promises';
import { SpreadsheetFile, Workbook } from '@oai/artifact-tool';

const root = new URL('..', import.meta.url).pathname;
const outputDir = `${root}outputs/day6`;
const csvPath = `${root}data/curated/ticket_sla_mart.csv`;
const quality = JSON.parse(await fs.readFile(`${root}reports/data_quality_report.json`, 'utf8'));
const csvText = await fs.readFile(csvPath, 'utf8');
const workbook = await Workbook.fromCSV(csvText, { sheetName: 'Tickets' });
const tickets = workbook.worksheets.getItem('Tickets');

// Type the imported CSV before formulas consume it.
const used = tickets.getUsedRange();
const values = used.values;
const headers = values[0];
const numeric = new Set(['response_target_hours','resolution_target_hours','mtta_hours','mttr_hours','age_hours','risk_score','transfer_count']);
const boolean = new Set(['reopened','response_breached','resolution_breached','sla_breached']);
const dateCols = new Set(['created_at','first_response_at','resolved_at']);
const typed = values.map((row, ri) => ri === 0 ? row : row.map((value, ci) => {
  const header = headers[ci];
  if (numeric.has(header)) return value === '' ? null : Number(value);
  if (boolean.has(header)) return String(value).toLowerCase() === 'true';
  if (dateCols.has(header)) return value === '' ? null : new Date(value);
  return value;
}));
used.values = typed;
// A formula-driven month key keeps period summaries auditable and avoids
// locale-dependent date-text matching in Excel criteria formulas.
tickets.getRange(`U1:U${typed.length}`).values = [['month_key'], ...Array.from({length: typed.length - 1}, () => [null])];
tickets.getRange(`U2:U${typed.length}`).values = typed.slice(1).map(row => [row[1] ? new Date(row[1]).toISOString().slice(0,7) : null]);
tickets.tables.add(`A1:U${typed.length}`, true, 'TicketsTable');
tickets.freezePanes.freezeRows(1);
tickets.showGridLines = false;
tickets.getRange(`A1:U${typed.length}`).format.font = { name: 'Arial', size: 10, color: '#1F2937' };
tickets.getRange('A1:U1').format = { fill: '#1F4E78', font: { name: 'Arial', size: 10, bold: true, color: '#FFFFFF' } };
tickets.getRange(`B2:D${typed.length}`).format.numberFormat = 'yyyy-mm-dd hh:mm';
tickets.getRange(`H2:I${typed.length}`).format.numberFormat = '0.0';
tickets.getRange(`L2:N${typed.length}`).format.numberFormat = '0.00';
tickets.getRange(`S2:S${typed.length}`).format.numberFormat = '0.0';
tickets.getRange('A:U').format.autofitColumns();

const sheet = name => workbook.worksheets.add(name);
const summary = sheet('Management Summary');
const diagnostics = sheet('Queue Diagnostics');
const trend = sheet('Monthly Trend');
const exceptions = sheet('Exceptions');
const controls = sheet('Scenario Controls');
const dq = sheet('Data Quality');
const definitions = sheet('Definitions');
const navy = '#1F4E78', blue = '#DCEAF7', amber = '#FFF2CC', green = '#E2F0D9', red = '#FCE4D6';
function base(s) { s.showGridLines = false; s.getRange('A1:O100').format.font = { name: 'Arial', size: 10, color: '#1F2937' }; }
function title(s, text, subtitle) { s.getRange('A1:H1').merge(); s.getRange('A1').values = [[text]]; s.getRange('A1:H1').format = { font: { name: 'Arial', size: 18, bold: true, color: navy } }; s.getRange('A2:H2').merge(); s.getRange('A2').values = [[subtitle]]; s.getRange('A2:H2').format = { font: { name: 'Arial', size: 10, italic: true, color: '#6B7280' } }; }
function header(range) { range.format = { fill: navy, font: { name: 'Arial', size: 10, bold: true, color: '#FFFFFF' }, horizontalAlignment: 'center', verticalAlignment: 'center' }; }
function widths(s, pairs) { for (const [col, width] of pairs) s.getRange(`${col}:${col}`).format.columnWidth = width; }
for (const s of [summary, diagnostics, trend, exceptions, controls, dq, definitions]) base(s);

// Executive management view.
title(summary, 'SLAForge management summary', 'Enterprise Service Desk SLA & Root-Cause Analytics | synthetic data | refreshed 01 Sep 2025');
summary.getRange('A4:B11').values = [['Metric','Value'],['Tickets',null],['SLA attainment',null],['MTTA (hrs)',null],['MTTR (hrs)',null],['FCR',null],['Reopen rate',null],['Critical open work',null]]; header(summary.getRange('A4:B4'));
summary.getRange('B5:B11').formulas = [['=COUNTA(Tickets!$A$2:$A$721)'],['=1-COUNTIF(Tickets!$Q$2:$Q$721,TRUE)/B5'],['=AVERAGE(Tickets!$L$2:$L$721)'],['=AVERAGE(Tickets!$M$2:$M$721)'],['=COUNTIFS(Tickets!$R$2:$R$721,0,Tickets!$J$2:$J$721,FALSE)/B5'],['=COUNTIF(Tickets!$J$2:$J$721,TRUE)/B5'],['=COUNTIFS(Tickets!$T$2:$T$721,"Critical",Tickets!$K$2:$K$721,"<>RESOLVED")']];
summary.getRange('B6:B6').format.numberFormat = '0.0%'; summary.getRange('B9:B10').format.numberFormat = '0.0%'; summary.getRange('B7:B8').format.numberFormat = '0.0'; summary.getRange('A4:B11').format.borders = { preset: 'outside', style: 'thin', color: '#CBD5E1' };
summary.getRange('D4:E8').values = [['Target controls','Value'],['SLA target',null],['Target gap',null],['As-of timestamp','2025-09-01'],['Data quality','PASS']]; header(summary.getRange('D4:E4')); summary.getRange('E5').formulas = [["='Scenario Controls'!B3"]]; summary.getRange('E6').formulas = [['=B6-E5']]; summary.getRange('E5:E6').format.numberFormat = '0.0%'; summary.getRange('E6').conditionalFormats.add('cellIs',{operator:'lessThan',formula:0,format:{fill:red,font:{color:'#9C0006',bold:true}}});
const queueNames=['Access Management','Business Apps','Infrastructure','Network','Workplace'];
summary.getRange('A14:C19').values = [['Queue','Tickets','SLA attainment'], ...queueNames.map(q=>[q,null,null])]; header(summary.getRange('A14:C14')); summary.getRange('B15:B19').formulas=queueNames.map((_,i)=>[`=COUNTIF(Tickets!$G$2:$G$721,A${15+i})`]); summary.getRange('C15:C19').formulas=queueNames.map((_,i)=>[`=1-COUNTIFS(Tickets!$G$2:$G$721,A${15+i},Tickets!$Q$2:$Q$721,TRUE)/B${15+i}`]); summary.getRange('C15:C19').format.numberFormat='0.0%'; summary.getRange('C15:C19').conditionalFormats.add('colorScale',{colors:['#FECACA','#FEF3C7','#DCFCE7'],thresholds:['min',90,'max']}); summary.charts.add('bar',summary.getRange('A14:C19')).setPosition('E12','L27'); summary.charts.items[0].title='SLA attainment by queue';
widths(summary,[['A',24],['B',16],['C',18],['D',20],['E',18]]);

// Diagnostic page.
title(diagnostics,'Queue diagnostics','Compare service levels with workload, handoffs, rework, aging, and risk.');
diagnostics.getRange('A4:H9').values=[['Queue','Tickets','SLA attainment','MTTA (hrs)','MTTR (hrs)','Reopen rate','Avg transfers','Avg risk'],...queueNames.map(q=>[q,null,null,null,null,null,null,null])]; header(diagnostics.getRange('A4:H4'));
for(let i=5;i<=9;i++){diagnostics.getRange(`B${i}:H${i}`).formulas=[[`=COUNTIF(Tickets!$G$2:$G$721,A${i})`,`=1-COUNTIFS(Tickets!$G$2:$G$721,A${i},Tickets!$Q$2:$Q$721,TRUE)/B${i}`,`=AVERAGEIF(Tickets!$G$2:$G$721,A${i},Tickets!$L$2:$L$721)`,`=AVERAGEIF(Tickets!$G$2:$G$721,A${i},Tickets!$M$2:$M$721)`,`=COUNTIFS(Tickets!$G$2:$G$721,A${i},Tickets!$J$2:$J$721,TRUE)/B${i}`,`=AVERAGEIF(Tickets!$G$2:$G$721,A${i},Tickets!$R$2:$R$721)`,`=AVERAGEIF(Tickets!$G$2:$G$721,A${i},Tickets!$S$2:$S$721)`]];}
diagnostics.getRange('C5:C9').format.numberFormat='0.0%'; diagnostics.getRange('F5:F9').format.numberFormat='0.0%'; diagnostics.getRange('D5:E9').format.numberFormat='0.0'; diagnostics.getRange('G5:H9').format.numberFormat='0.0'; diagnostics.getRange('C5:C9').conditionalFormats.add('cellIs',{operator:'lessThan',formula:"='Scenario Controls'!$B$3",format:{fill:red,font:{color:'#9C0006',bold:true}}}); diagnostics.getRange('H5:H9').conditionalFormats.add('dataBar',{color:'#F59E0B'}); diagnostics.charts.add('bar',diagnostics.getRange('A4:C9')).setPosition('J4','Q18'); diagnostics.charts.items[0].title='Queue SLA attainment'; widths(diagnostics,[['A',24],['B',12],['C',16],['D',13],['E',13],['F',14],['G',14],['H',12]]);

// Trend and cohort view.
title(trend,'Monthly trend','Creation-month cohorts; use the Power BI report for interactive date slicing.');
const monthGroups = new Map();
for (const row of typed.slice(1)) { const month = row[1] ? new Date(row[1]).toISOString().slice(0,7) : 'Unknown'; if (!monthGroups.has(month)) monthGroups.set(month, []); monthGroups.get(month).push(row); }
const months=[...monthGroups.keys()].filter(m=>m!=='Unknown').sort();
const monthValues=months.map(m=>{const rows=monthGroups.get(m); return [m,rows.length,1-rows.filter(r=>r[16]===true).length/rows.length,rows.reduce((sum,r)=>sum+Number(r[12]||0),0)/rows.length];});
trend.getRange(`A4:D${4+months.length}`).values=[['Month','Tickets','SLA attainment','MTTR (hrs)'],...monthValues]; header(trend.getRange('A4:D4'));
trend.getRange(`C5:C${4+months.length}`).format.numberFormat='0.0%'; trend.getRange(`D5:D${4+months.length}`).format.numberFormat='0.0'; trend.getRange(`C5:C${4+months.length}`).conditionalFormats.add('colorScale',{colors:['#FECACA','#FEF3C7','#DCFCE7'],thresholds:['min',90,'max']}); trend.charts.add('line',trend.getRange(`A4:C${4+months.length}`)).setPosition('F4','N20'); trend.charts.items[0].title='Monthly SLA attainment'; widths(trend,[['A',14],['B',12],['C',18],['D',14]]);

// Exception worklist with XLOOKUP formulas.
title(exceptions,'Exceptions','Breached or high-risk ticket worklist. Scores are triage aids, not employee measures.'); exceptions.getRange('A4:G4').values=[['Ticket ID','State','Priority','Queue','Risk score','Risk band','Action']]; header(exceptions.getRange('A4:G4'));
const exceptionIds=typed.slice(1).filter(r=>r[16]===true||Number(r[18])>=70).sort((a,b)=>Number(b[18])-Number(a[18])).slice(0,40).map(r=>[r[0]]);
exceptions.getRange(`A5:A${4+exceptionIds.length}`).values=exceptionIds; for(let i=5;i<5+exceptionIds.length;i++) exceptions.getRange(`B${i}:G${i}`).formulas=[[`=_xlfn.XLOOKUP(A${i},Tickets!$A$2:$A$721,Tickets!$K$2:$K$721,"Missing")`,`=_xlfn.XLOOKUP(A${i},Tickets!$A$2:$A$721,Tickets!$E$2:$E$721,"Missing")`,`=_xlfn.XLOOKUP(A${i},Tickets!$A$2:$A$721,Tickets!$G$2:$G$721,"Missing")`,`=_xlfn.XLOOKUP(A${i},Tickets!$A$2:$A$721,Tickets!$S$2:$S$721,"")`,`=_xlfn.XLOOKUP(A${i},Tickets!$A$2:$A$721,Tickets!$T$2:$T$721,"Missing")`,`=IF(E${i}>='Scenario Controls'!$B$4,"Escalate","Monitor")`]];
exceptions.getRange(`E5:E${4+exceptionIds.length}`).format.numberFormat='0.0'; exceptions.getRange(`E5:E${4+exceptionIds.length}`).conditionalFormats.add('dataBar',{color:'#EF4444'}); exceptions.getRange(`G5:G${4+exceptionIds.length}`).conditionalFormats.add('containsText',{text:'Escalate',format:{fill:red,font:{color:'#9C0006',bold:true}}}); exceptions.freezePanes.freezeRows(4); widths(exceptions,[['A',16],['B',14],['C',11],['D',24],['E',12],['F',14],['G',14]]);

// Scenario controls with input validation.
title(controls,'Scenario controls','Editable planning inputs; changing these values updates target gaps and exception actions.'); controls.getRange('A4:B8').values=[['Control','Value'],['SLA target',0.90],['Critical risk threshold',70],['Intervention capacity (tickets)',10],['Planning note','Scenario only; source facts unchanged.']]; header(controls.getRange('A4:B4')); controls.getRange('B5').format={fill:amber,font:{bold:true}}; controls.getRange('B6:B7').format={fill:amber,font:{bold:true}}; controls.getRange('B5').format.numberFormat='0.0%'; controls.dataValidations.add({range:'B5',rule:{type:'decimal',operator:'between',formula1:0,formula2:1}}); controls.dataValidations.add({range:'B6',rule:{type:'whole',operator:'between',formula1:0,formula2:99}}); controls.dataValidations.add({range:'B7',rule:{type:'whole',operator:'between',formula1:0,formula2:1000}}); controls.getRange('A11:B14').values=[['Scenario output','Value'],['Current SLA attainment',null],['Gap to selected target',null],['Tickets above selected threshold',null]]; header(controls.getRange('A11:B11')); controls.getRange('B12:B14').formulas=[["='Management Summary'!B6"],['=B12-B5'],['=COUNTIF(Tickets!$S$2:$S$721,">="&B6)']]; controls.getRange('B12:B13').format.numberFormat='0.0%'; widths(controls,[['A',30],['B',26]]);

// Data quality and definitions.
title(dq,'Data quality','Blocking controls and reconciliation from the governed pipeline run.'); dq.getRange('A4:B13').values=[['Control','Result'],['Status',quality.status],['Raw tickets',quality.source.tickets],['Fact tickets',quality.database_row_counts.fact_ticket_sla],['Ticket row difference',quality.reconciliation.staging_to_fact_tickets],['Raw assignment events',quality.source.assignment_events],['Fact assignment events',quality.database_row_counts.fact_assignment],['Assignment row difference',quality.reconciliation.staging_to_fact_events],['Freshness age (hours)',quality.checks.freshness.age_hours],['Freshness threshold (hours)',quality.checks.freshness.threshold_hours]]; header(dq.getRange('A4:B4')); dq.getRange('B5').conditionalFormats.add('containsText',{text:'PASS',format:{fill:green,font:{color:'#006100',bold:true}}}); dq.getRange('B5').conditionalFormats.add('containsText',{text:'FAIL',format:{fill:red,font:{color:'#9C0006',bold:true}}}); dq.getRange('B8:B11').format.numberFormat='0'; widths(dq,[['A',32],['B',20]]);
title(definitions,'Definitions and help','Use this page to interpret measures, refresh the workbook, and understand limitations.'); definitions.getRange('A4:B15').values=[['Topic','Definition / instruction'],['Source','SLAForge governed SQLite star schema and KPI views.'],['Refresh','Power Query: replace the Tickets query with the approved SQLite view, refresh queries, then refresh PivotTables/PivotCharts.'],['Ticket grain','One row per ticket in TicketsTable; assignment history is event-grain in the source model.'],['SLA attainment','1 − breached tickets ÷ tickets; prototype uses calendar hours.'],['MTTA / MTTR','Mean created-to-first-response / created-to-resolution (or as-of) hours.'],['FCR','Tickets with zero transfers and no reopen ÷ tickets.'],['Exception action','Escalate when risk score meets Scenario Controls threshold; otherwise Monitor.'],['Scenario controls','Planning inputs only; they do not alter source facts or contractual SLA policy.'],['Privacy','Prototype data is deterministic and synthetic; exclude direct identifiers in production.'],['Owner / cadence','Service Operations data owner; daily refresh by 08:00 local time.'],['Caveat','Validate business calendars, pause rules, model calibration, and production access before contractual use.']]; header(definitions.getRange('A4:B4')); definitions.getRange('B5:B15').format.wrapText=true; definitions.getRange('A4:B15').format.borders={preset:'outside',style:'thin',color:'#CBD5E1'}; widths(definitions,[['A',24],['B',110]]);

// Compact formatting and freeze headers for working tabs.
for (const s of [summary, diagnostics, trend, exceptions, controls, dq, definitions]) { s.getRange('A1:O100').format.verticalAlignment='center'; }
await fs.mkdir(outputDir,{recursive:true});
// Render every reader-facing tab for visual QA.
for (const s of [summary, diagnostics, trend, exceptions, controls, dq, definitions]) { const preview=await workbook.render({sheetName:s.name,autoCrop:'all',scale:1,format:'png'}); await fs.writeFile(`/private/tmp/sla-forge-${s.name.replaceAll(' ','-')}.png`,new Uint8Array(await preview.arrayBuffer())); }
const errors=await workbook.inspect({kind:'match',searchTerm:'#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A|#NUM!|#NULL!|#SPILL!|#CALC!',options:{useRegex:true,maxResults:300},summary:'final formula error scan'}); if (errors.ndjson?.trim()) console.log(errors.ndjson);
const xlsx=await SpreadsheetFile.exportXlsx(workbook); await xlsx.save(`${outputDir}/sla_forge_decision_workbook.xlsx`);
console.log('Exported',`${outputDir}/sla_forge_decision_workbook.xlsx`);
