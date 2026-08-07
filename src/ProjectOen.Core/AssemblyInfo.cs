using System.Runtime.CompilerServices;

// docs/06 afsnit 5: "Kun ScenarioDirector maa skifte scenariofase."
// Den regel haandhaeves med 'internal set' paa Phase og Day, saa ingen anden
// produktionskode kan omgaa den. Testene har brug for at kunne stille en
// tilstand op direkte - derfor denne, og kun denne, undtagelse.
[assembly: InternalsVisibleTo("ProjectOen.Core.Tests")]
