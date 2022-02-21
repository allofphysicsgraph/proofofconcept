
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
base might incur more work and cognitive load that would be
beneficial. I'd be happy if someone forks the code and rewrites
everything. I'm wary of integrating small and medium refactoring
because there's likely to be a big gap in terms of both skill and how
each person thinks about the composition of core functions and
workflow.

# Design Philosophy for the Physics Derivation Graph

* Minimal reliance on external dependencies. Because I want this project to be durable, and because I don't want to have to constantly be updating this project to keep it working, I'm willing to invest in initial implementation even at the risk of a bug or lacking a feature in another library. 
* Easy to read the source code for the project. I don't expect to complete this project, so if it is to be durable, it will be read by other people.
* Open source. I want others to be able to leverage this investment. 
* Free (no cost to users). I want to minimize the barrier to entry and make the work accessible to the largest audience.
* No advertising. I don't have a need for money to be generated and am willing to pay website hosting costs and domain registration costs.
* Limit tracking of users. I don't need to determine user behavior beyond what appears in weblogs. Logging in to add/modify/delete content is relevant to address potential vandalism. 
* No profit generation. I don't have a need to make money from this effort. 
* Long-term durability of the code and website. No browser-specific hacks. Minimize reliance on version-specific features
* Implement the code and website at a level below the maintainer's competency. 

# Current Blockers

* adding new content is a tedius process even before the content is ready to enter into the database
* the website provides a labourous process for adding content to the database
* identifying which derivations are most relevant to invest in is tough
* how to check math that SymPy doesn't support
* domain expertise in Physics and Math is relevant, as is knowledge of Latex. 
* The relation between the visual representation (Latex) and Computer Algebra System (Sympy) is manual and unchecked
* how relevant is the CAS compared to the visual representation? If a step is wrong but the derivation's outcome is correct, what's the impact?
* irrelevance of graph visualizations for individual derivations and the complete graph and simplifications of the complete graph
* what graph queries would be useful? Is that worth supporting?
* what threshold of content is necessary for usefulness to various audiences? (Students, researchers, lay people)
* A lot of MathJax on a webpage makes pages slower to render; https://github.com/allofphysicsgraph/proofofconcept/issues/173
