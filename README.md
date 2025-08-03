# ids

This document describes approach for generaiting an unguessable, unique and
human friendly resource dentifiers.


## Rationale

Predictable identifiers in APIs introduce both security and information
disclosure risks. Even if proper permission validation is implemented,
predictable ID formats increase the impact of any vulnerability, especially
those involving broken access control. This section explains why resource
identifiers should not be easily guessable and justifies the need for random or
obfuscated IDs.

### 1. Security: Mitigating Enumeration Attacks

Predictable IDs (e.g., sequential integers like /users/1001, /users/1002, etc.)
make APIs more vulnerable to enumeration attacks. In such attacks, an adversary
can programmatically iterate over ID values to discover or manipulate
unauthorized resources.

Even with proper access control, a single overlooked flaw (e.g., an insecure
endpoint or a missing permission check) can be exploited at scale if IDs are
predictable. On the contrary, when IDs are unpredictable, attackers cannot
easily guess valid identifiers and are limited in what they can access—even if
a vulnerability exists.

This pattern is listed in the recommendation about how to prevent
[API1:2023 Broken Object Level Authorization](https://owasp.org/API-Security/editions/2023/en/0xa1-broken-object-level-authorization/)

### 2. Privacy: Hiding Business Metrics

Sequential or timestamp-based IDs may unintentionally leak business-sensitive
information, such as:

- The total number of users or entities in the system.
- The rate at which new entities are created (e.g., orders per hour).
- Approximate registration times.

Competitors or unauthorized users could monitor these patterns to gain insights
about your system’s usage or growth.

### 3. Predictability vs. Collisions

One common mitigation is to use random identifiers (e.g., UUIDs or base-N
encoded random strings), which greatly reduce the chance of an attacker
guessing a valid ID. However, random ID generation introduces the risk of
collisions—generating the same ID more than once—unless the ID space is
sufficiently large.

This leads to a tradeoff:

- Shorter IDs are more user-friendly but increase the collision probability.
- Longer IDs reduce collisions but are less convenient for humans.

The remainder of this document analyzes this tradeoff quantitatively and
proposes a collision-free and non-predictable approach that enables the use of
short, human-friendly IDs without requiring large ID spaces or introducing
significant storage or UX burden.

## The Cost of Randomness: Collisions and Length

Using randomly generated IDs can improve unpredictability and security, but it
comes at a cost: the possibility of collisions—i.e., generating the same ID
more than once. To keep this risk acceptably low, the ID space must be
sufficiently large, which directly affects the length of the ID.

### Probability of Collision-Free Random ID Generation

Assume we want to generate $K$ unique identifiers by randomly sampling from a
set of $N$ possible IDs (e.g., all strings of a given length from a fixed
alphabet). We are interested in the probability $P$ that no collisions occur
during this process.

The total number of ways to generate $K$ IDs (allowing collisions) is:

$$N^K$$

The number of ways to choose $K$ distinct IDs from the set of $N$ is:

$$N(N-1)...(N-K+1)=\frac{N!}{(N-K)!}$$

Thus, the exact probability of generating $K$ distinct IDs without collisions is:

$$P=\frac{N(N-1)...(N-K+1)}{N^K}$$

This formula is related to the well-known [Birthday Problem](https://en.wikipedia.org/wiki/Birthday_problem).
For large $N$ and reasonably small $K$, this probability can be approximated by:

$$P\approx\mathrm{e}^{-\frac{K^2}{2N}}$$

Therefore, the probability of at least one collision during the generation of
$K$ random IDs is:

$$1-P=1-\mathrm{e}^{-\frac{K^2}{2N}}$$

This approximation is extremely useful in practice, as it allows us to estimate
the required ID space size $N$ for a given number of expected IDs $K$, while
keeping the collision probability within acceptable bounds.


### Human-Friendly Alphabet

To keep IDs readable and writable by humans, we restrict the character set to
avoid visually confusing characters (e.g., O, 0, I, l, 1, J). A widely accepted
human-friendly alphabet is:

$$
\text{0123456789ABCDEFGHKMNPQRSTUVWXYZ}
$$

This gives us 32 symbols. If we choose an ID length of $L$ characters, the
total number of unique IDs we can represent is:

$$N=32^L$$

Let’s examine how many characters we need in a 32-symbol alphabet to safely
generate $K=10^9$ random IDs without significant risk of collisions.

| L     | P       |
| ----- | ------- |
| 5     | 100%    |
| 6     | 100%    |
| 7     | 100%    |
| 8     | 100%    |
| 9     | 100%    |
| 10    | 100%    |
| 11    | 99%     |
| 12    | 35%     |
| 13    | 1.3%    |
| 14    | 0.04%   |
| 15    | 0.0013% |


As shown, to get below a 0.01% collision risk when generating $K=10^9$ IDs,
you need at least 15 characters. While secure and robust, this length may be
inconvenient for users who need to type or read these IDs frequently.

### Tradeoff: Uniqueness vs Brevity

On the other hand, if we are not using randomness but instead sequential
integers (e.g., PostgreSQL SERIAL or BIGSERIAL), we don't need to worry about
collisions. To represent all integers in the range $[1, 2^{31}-1]$ in our
32-character alphabet, we only need:

$$L=7\text{ because }32^{7}=2^{35}>2^{31}-1$$

So, while random IDs require 15+ characters to avoid collisions, deterministic
integer-based IDs need only 7 characters to represent the same number of records.

But how to make sequential IDs non predictable? One of the possible solution is
to get next number from the sequence and encrypt it. Encryption function $e$ by
it's nature must map $x \in X \rightarrow e(x) \in Y$ so that for the given
$y=e(x)$ each $x \in X$ must have about equal probability to be a clear text
for the given encrypted text $y$ (of course without knowing the private key).

### RSA encryption

Let's explore how RSA encryption can provide pseudo randomization for and
integer sequence. Let's denote $N$ as the total amount of IDs that is considered
as enough, $L$ - is the ID length required to encode any ID in range $1..N$ in
an alphabet of $X$ characters. Then, in notations of the [article](https://en.wikipedia.org/wiki/RSA_(cryptosystem)),
if we chose $n = pq > N \wedge n \le A^L$, then the encryption function will be
the bijective function $R: 1..n-1 \rightarrow 1..n-1$. The encryption function
obviously must be bijective in order to be able to decrypt clear text from any
legal encrypted text.

Let $encode$ will be the function that encodes a number from range $R$ in an
alphabet A. Let $encrypt$ will be the RSA-encryption function, $decode$, $decrypt$
will be the functions reverse to the functions $encode$, $encrypt$ respectively,
$next() \rightarrow 1..N$ the function that produces the sequential numbers.

Then ID generation algorithm is the following: $id = encode(encrypt(next()))$.
In order to get the original value $v$ returned by function $next$ there needs
to be calculated: $decrypt(decode(id))$.

### Implementation

If we consider a PostgreSQL integer sequence that produces primary keys in range
$1 .. 2^{31}-1$ and alphabet of 32 symbols defined above, then the required ID
length, as we have seen above most be $7$.

Now we chose primes $p$, $q$ so that $n=pq > 2^{31}-1$, the last condition is
crucial in order to ensure any number from the given interval $1 .. 2^{31}-1$
can be encrypted. Then we chose $e$ so that $\gcd(e, \phi(n)) = 1$ and
calculate $d$ so that $ed \equiv 1 mod \phi(n)$


## References

1. https://owasp.org/API-Security/editions/2023/en/0xa1-broken-object-level-authorization/
