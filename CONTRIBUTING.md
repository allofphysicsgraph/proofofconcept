
# Contributing to the _Physics Derivation Graph_

Thanks for your interest in improving the project!


To contribute, you can 
 * open a <a href="https://github.com/allofphysicsgraph/proofofconcept/issues/new?assignees=&labels=&template=bug_report.md&title=">bug report</a>
 * open a <a href="https://github.com/allofphysicsgraph/proofofconcept/issues/new?assignees=&labels=&template=feature_request.md&title=">feature request</a>
 * suggest other projects that are similar or relevant by <a href="http://derivationmap.net/faq?referrer=CONTRIBUTING#contact">contacting the developer</a>
 * [modify the code](https://github.com/allofphysicsgraph/proofofconcept/fork) and create alternative implementations
 * ask a question that is not posted on [the FAQ](https://allofphysicsgraph.github.io/proofofconcept/site/faq.html)

Development is done in Docker containers. Changes to the code should run in a Docker container. Novel architecture suggestions should run in a container.  If you can create a minimal Dockerfile and Makefile that shows what your demo does, then I can reliably recreate the demo.



Having multiple developers working on independent (but coordinated)
aspects would be beneficial, both because I don't have the capacity to
explore all avenues and because I don't have the skills in all areas.
I think leveraging what each person is good at and interested in would
yield the most benefit. For example, if you work on SymPy grammar or
formal proofs or graph display or graph search, all of those provide
value I wouldn't otherwise chase.

Coordinating with another developer on core aspects of the code
base would incur more work and cognitive load that would be
beneficial. I'd be happy if someone forks the code and rewrites
everything. I'm wary of integrating small and medium refactoring
because there's likely to be a big gap in terms of both skill and how
each person thinks about the composition of core functions and
workflow.

