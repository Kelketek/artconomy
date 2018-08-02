<template>
  <v-container>
    <v-tabs v-model="tab" fixed-tabs>
      <v-tab href="#tab-about">
        About
      </v-tab>
      <v-tab href="#tab-buying-and-selling">
        Buying/Selling
      </v-tab>
      <v-tab href="#tab-other">
        Other/Misc
      </v-tab>
    </v-tabs>
    <v-tabs-items v-model="tab">
      <v-tab-item id="tab-about">
        <v-expansion-panel v-model="aboutTab">
          <v-expansion-panel-content>
            <div slot="header"><strong>What is Artconomy?</strong></div>
            <v-card>
              <v-card-text>
                <p>
                Artconomy is your online marketplace for custom art, especially art of your characters!
                We provide a safe platform for artists and commissioners to work with each other without the frustration
                of ad-hoc solutions to tracking outstanding work, finding available artists, and tracking character profiles.
                </p>
                <p>
                  Artconomy provides many features such as:
                </p>
                <ul>
                  <li>Character Profiles</li>
                  <li>Stores for artists to sell commissions</li>
                  <li>Artist availability tracking</li>
                  <li>Escrow services for commissions-- artists don't get paid unless the work is complete, and commissioners cannot back out once they've sent payment</li>
                  <li>Contract agreements for both parties to refer to in case disagreements arrise</li>
                  <li>Dispute resolution services between artists and commissioners</li>
                  <li>Character transfers/sales</li>
                  <li>...And more!</li>
                </ul>
              </v-card-text>
            </v-card>
          </v-expansion-panel-content>
          <v-expansion-panel-content>
            <div slot="header"><strong>Does Artconomy cost money to use?</strong></div>
            <v-card>
              <v-card-text>
                <p>Artconomy is <strong>FREE</strong> to use. Your character gallery is <strong>FREE</strong>, running a shop as an artist is <strong>FREE</strong>.</p>

                <p>Artconomy only collects fees for premium services and upon actual sales. It costs you nothing to get
                  started commissioning on Artconomy, and artists pay fees for completed sales.</p>

                <p>We don't make money if our artists don't make money and our commissioners aren't served.
                  This gives us an incentive to make the best platform we can for both groups.</p>
              </v-card-text>
            </v-card>
          </v-expansion-panel-content>
          <v-expansion-panel-content>
            <div slot="header"><strong>Who runs Artconomy?</strong></div>
            <v-card>
              <v-card-text>
                <p>Our team consists of people who are passionate about art.</p>
                <h3>CEO and Lead Developer: Fox Danger Piacenti</h3>
                <p>Fox is a long term online role player who has had a passion to see characters
                  come alive online. He has worked as a lead developer, administrator, and director in the recreational
                  and professional spheres.</p>
                <p>Fox began work on Artconomy upon observing the difficulties encountered when commissioning, and
                  realizing that he rarely commissioned online but frequently did at creative conventions,
                  where one could meet face-to-face with artists. He wanted to create a service where it was as easy
                  to commission online as it was in person.</p>
                <h3>Marketing and Public Relations Director: Eris Autumn Griffon</h3>
                <p>Eris is <em>also</em> a longterm online role player and her life is filled with artists, so she's
                  always had a passion to make art more accessible for everyone and to see characters come alive online!
                  She's served six years in the US Navy, and also worked in a paper factory, handed out samples, worked
                  at a newspaper, crewed tall ships, and worked various IT-related jobs.</p>
                <p>Eris came to Artconomy when she heard about it from her friend Fox and offered to help with the
                  'people' side of things. She's been managing Artconomy's social media presence, recruiting and
                  coordinating of testers, mailing list, and things like that. Outside of her two jobs, she spends her
                  time with RP, video games, and her artist/musician girlfriend.</p>
                <p><strong>And yes, those are our real legal names. You have to be a little crazy to get into this
                  line of work.</strong></p>
              </v-card-text>
            </v-card>
          </v-expansion-panel-content>
        </v-expansion-panel>
      </v-tab-item>
      <v-tab-item id="tab-buying-and-selling">
        <v-expansion-panel v-model="buySellTab">
          <v-expansion-panel-content>
            <div slot="header"><strong>How do I buy commissions on Artconomy?</strong></div>
            <v-card>
              <v-card-text>
                <p>
                  To buy a commission on Artconomy, first create any characters you wish to have
                  portrayed in
                  <router-link
                      :to="{name: 'Profile', params: {username: viewer.username, tabName: 'characters'}}"
                      v-if="viewer.username"
                  >
                    your characters tab on your profile.
                  </router-link><span v-else>your characters tab on your profile.</span>
                  Describe your characters detail as you can, and/or upload any artwork that has already been
                  completed of your character(s) to give the artist a reference to work with.
                  If you don't want any characters portrayed, you may skip this step.
                </p>
                <p>
                  Next, find an artist who is open. You may check if any of the artists you are currently watching are
                  open by clicking the 'Who's Open?' link in the sidebar. You may also check the recently created
                  products on the front page, or you may search in the search bar.
                </p>
                <p>
                  Once you have found a product that you like, click the Order button on the product page and
                  fill out the provided form.
                </p>
                <p>
                  The artist will then review your request, ask any questions or make comments, and then will finalize
                  the price if they are willing to complete the piece or reject the order if they are not.
                </p>
                <p>
                  Once the artist has approved your request, you will be able to pay for the order. We will hold onto
                  the money until the artist completes the work. They may upload revisions for your approval. Please
                  provide comments to the artist when revisions are uploaded to ensure the result is what you are hoping
                  for.
                </p>
                <p>
                  Once the artist has completed the work, you may approve the final piece, and the artist will be paid.
                  Then you can rate your artist, and add the final piece to your gallery if you like.
                </p>
              </v-card-text>
            </v-card>
          </v-expansion-panel-content>
          <v-expansion-panel-content>
            <div slot="header"><strong>How do I sell commissions on Artconomy?</strong></div>
            <v-card>
              <v-card-text>
                <p>
                  To sell commissions on Artconomy, you must first
                  <router-link
                      :to="{name: 'Settings', params: {username: viewer.username, tabName: 'payment', subTabName: 'disbursement'}}"
                      v-if="viewer.username"
                  >
                    configure your bank account
                  </router-link><span v-else>configure your bank account</span> so that we can send you
                  any money you earn. Please see the question below about bank accounts.
                </p>
                <p>
                  Once your banks account is set up, you may create a product. Click the 'My Products' link in the
                  sidebar to create a product. Fill out the provided form and your product will be listed.
                </p>
                <p>
                  After you have created a product, it will be listed on your profile page and on the recently created
                  products list on the front page. Buyers may then commission you by clicking on it.
                </p>
                <p>
                  Once you have an order, review the commissioner's request and make sure you understand it fully.
                  If you are satisfied you understand the commissioner's requirements and wish to take on the work,
                  add any price adjustments necessary, such as those for shipping the original if you
                  include that with your product, or any extra work that their request requires.
                  Finally, hit the approve button.
                </p>
                <p>
                  The commissioner will then review the offer and pay for it if they find it acceptable.
                  You should then begin the work as soon as you are able, uploading any revisions along the way. When
                  you are finished, submit your final piece.
                </p>
                <p>
                  The commissioner will then review and approve your work. Once approved, you will receive the money
                  that has been held, minus Artconomy's fees.
                </p>
              </v-card-text>
            </v-card>
          </v-expansion-panel-content>
          <v-expansion-panel-content>
            <div slot="header"><strong>How are disputes handled?</strong></div>
            <v-card>
              <v-card-text>
                <p>
                  When a commission is finished, or an extended period between the task's acceptance and its
                  completion has elapsed, a commissioner will have the option to file a dispute. Disputes will come up
                  for review by our staff.
                </p>
                <p>
                  Disputes are evaluated on a case-by-case basis. Our staff will review the order's history, and ask any
                  additional questions as needed before making any decisions.
                </p>
                <p>One or more of the following conditions will make an order eligible for a refund:</p>
                <ul>
                  <li>The artist has taken an extraordinary amount of time beyond estimate to complete the work (this will not be considered if the final is already delivered by the time the dispute is filed)</li>
                  <li>The artist has drawn something <strong>severely</strong> under their standard quality of work as depicted in their gallery.</li>
                  <li>The artist has drawn something completely different than what a reasonable reader would have expected the commission notes to require.</li>
                  <li>Sales involving original goods being shipped do not arrive or are damaged. Recepient must provide proof of damage. Artists are expected to use trackable forms of shipment and buy insurance to cover damage so that they may claim the difference from their carrier.</li>
                </ul>
                <p>The following conditions will <strong>NOT</strong> make an order eligible for a refund:</p>
                <ul>
                  <li>The artist is moderately over estimate.</li>
                  <li>The final piece has flaws which were in previously posted revisions that were either commented on by the commissioner or which the commissioner had time for comment and no comment was made.</li>
                  <li>The piece is within reasonable variance of the artist's history of quality, but it is not quite what the commissioner hoped for.</li>
                  <li>The final piece has minor differences from the description, or differences that could result from reasonable mistakes when reading the commission notes.</li>
                </ul>
                <p>
                  The above cases, while regrettable, will not be warranted against by Artconomy for the cost of the
                  commission price. The commissioner is free to include any information about their commissioning
                  experience when rating the artist.
                </p>
              </v-card-text>
            </v-card>
          </v-expansion-panel-content>
          <v-expansion-panel-content>
            <div slot="header"><strong>What banks can be linked to Artconomy?</strong></div>
            <v-card>
              <v-card-text>
                <p>
                  At present, only US Bank accounts can be integrated with Artconomy. We are looking into ways to
                  support European and other banks but do not currently have a method of doing so.
                </p>
              </v-card-text>
            </v-card>
          </v-expansion-panel-content>
          <v-expansion-panel-content>
            <div slot="header"><strong>How can I manage my workload with Artconomy's tools?</strong></div>
            <v-card>
              <v-card-text>
                <p>
                  Artconomy understand the problems artists have with managing their workload and communicating with
                  commissioners. We've come up with a number of art-specific tools to help with managing your workload.
                </p>
                <p>
                  Workload management begins with your
                  <router-link
                      :to="{name: 'Settings', params: {username: viewer.username, tabName: 'options'}}"
                      v-if="viewer.username"
                  >
                    Maximum Load, configurable in your settings.
                  </router-link>
                  <span v-else>
                    Maximum Load, configurable in your settings.
                  </span>
                  Your maximum load is a number of 'points' you can assign to tasks. For instance, if you have a
                  maximum load of 10, and sell sketches with a task weight of 2, Artconomy will close commissions once
                  you have five of them.
                </p>
                <p>
                  Artconomy is able to track multiple products' workloads. If you also sell full color pieces and set
                  their task weight as 5, you could have one full color commission and two sketches (totalling 9 points)
                  before commissions would close, since both a sketch and a full color would put your workload over 10
                  at that point. You could also have two full color commissions to use up all 10 points.
                </p>
                <p>
                  In addition to this, you may also specify the 'Max at Once' setting for a product. If you never want to
                  do more than two sketches at a time, you would set this to 2. This will make sure that if you already
                  have two sketches accepted, Artconomy will delist sketches from your store so you don't receive more
                  requests for them.
                </p>
                <p>
                  Artconomy manages when you are considered 'open' for commissions, sending alerts to Portrait and
                  Landscape subscribers when you are available. Note that you may still be closed for commissions even
                  if you have some workload to spare. See
                  <router-link
                      :to="{name: 'FAQ', params: {tabName: 'buying-and-selling', subTabName: 'why-commissions-disabled'}}"
                  >
                    'Why are my Commissions Disabled?'
                  </router-link>
                  for more information as to why this may happen.
                </p>
                <p>
                  All orders offer a direct communication line with your commissioner.
                  Commenting on an order sends an email alert and notification to the commissioner for them to review.
                  This ensures that you do not have to keep individual track of customers' email addresses to get a
                  hold of them. Feel free to comment and ask questions to make sure you can give your customers the best
                  experience possible!
                </p>
              </v-card-text>
            </v-card>
          </v-expansion-panel-content>
          <v-expansion-panel-content>
            <div slot="header"><strong>What are Placeholder Orders?</strong></div>
            <v-card>
              <v-card-text>
                <p>
                  Artconomy wants to help you manage your workload, but it won't be able to do this very effectively if
                  it insists that all of your commissions are made through its order forms. Sometimes you have projects
                  that are commissioned offline or through another service and need to keep track of them.
                </p>
                <p>
                  Placeholder orders allow you to keep track of these projects and have them count against your
                  current load so that customers don't commission you when you're already too busy.
                </p>
                <p>
                  Placeholder orders are not, however, fully featured orders in Artconomy. You cannot, for instance,
                  comment directly to your customers from them, take payment, or utilize Artconomy's dispute resolution
                  services through Placeholder Orders. They are for tracking your workload only, and keeping track of
                  any notes you may have while working on the projects you've made them for.
                </p>
              </v-card-text>
            </v-card>
          </v-expansion-panel-content>
          <v-expansion-panel-content>
            <div slot="header"><strong>What are Order Tokens?</strong></div>
            <v-card>
              <v-card-text>
                <p>
                  Sometimes you may have a special project or in person sale which you want to track fully through
                  Artconomy but it would normally not be allowed via your load settings or because your commissions are
                  marked closed. For example, if you're at a convention and taking commissions from con-goers, you might
                  not want commissions created during the event to be restricted, since you'll be doing them
                  within days or hours and returning to your normal workload when you return home.
                </p>
                <p>
                  Artconomy allows you to send an Order Token to an email address of your choice. Users can then use the
                  token to place an order when they otherwise could not, and it will end up in your queue to complete.
                </p>
                <p>
                  You are advised to be judicious when using Order Tokens-- if overused, they can cause you to be
                  overloaded with work and cause customer service issues that will result in low ratings and possible
                  disputes if tasks fall far behind their estimated completion date.
                </p>
              </v-card-text>
            </v-card>
          </v-expansion-panel-content>
          <v-expansion-panel-content>
            <div slot="header"><strong>Why are my commissions disabled?</strong></div>
            <v-card>
              <v-card-text>
                <p>
                  Artconomy uses a smart algorithm to help determine if you should be considered open for commissions.
                  On your sales page, you will see information about your current commission status and any reasons
                  why you may not be open. Some of these reasons may include:
                </p>
                <ul>
                  <li>You have marked yourself as 'commissions closed' in your settings.</li>
                  <li>You are at or over your Maximum Load, also configurable in your settings.</li>
                  <li>You are under your maximum load, but none of your products will fit in the remaining workload.</li>
                  <li>You are under your maxumum load, but any products which DO fit in the remaining workload have
                    already reached their 'max at once' limit.
                  </li>
                  <li>
                    You are under your maximum load, do not have commissions closed, and have viable products,
                    but you still have open requests left over from the last time you were open for commissions. You
                    must accept or reject these before you will be able to take new orders, in order to reduce the
                    incidence of customer service issues.
                  </li>
                </ul>
              </v-card-text>
            </v-card>
          </v-expansion-panel-content>
          <v-expansion-panel-content>
            <div slot="header"><strong>Why not use PayPal?</strong></div>
            <v-card>
              <v-card-text>
                <p>
                  PayPal is a popular service used by Artists to take payments from commissioners,
                  however, it has several key limitations:
                </p>
                <ul>
                  <li>PayPal has separate policies for business and personal use that can be confusing.</li>
                  <li>PayPal's dispute resolution is limited and not well suited for art, especially when using their
                    personal service.
                  </li>
                  <li>PayPal has been known to suspend accounts with little recourse or comment.</li>
                  <li>PayPal has a strict policy against mature content. Artists found taking payment for mature
                    commissions may find their accounts abruptly closed.</li>
                </ul>
                <p>
                  Artconomy is built with the needs of commissioners and artists in mind, and specializes in the needs of both.
                  PayPal's limitations also prevent it from being a backend for Artconomy to take payments, so we are
                  unable to accept payments via PayPal.
                </p>
              </v-card-text>
            </v-card>
          </v-expansion-panel-content>
          <v-expansion-panel-content>
            <div slot="header"><strong>How does Artconomy compare to Patreon?</strong></div>
            <v-card>
              <v-card-text>
                <p>
                  Patreon is a popular platform for artists that allows them to receive monthly
                  contributions from patrons. Patrons are also able to receive exclusive rewards for being monthly donors.
                </p>
                <p>
                  Artconomy is considering adding functionality like Patreon has in the future. We believe that services
                  like Patreon and Artconomy are best used together to help artists achieve their goals of
                  self-sufficiency from their artistic work.
                </p>
                <p>
                  Patreon has a significant limitation however--
                  <a href="https://en.wikipedia.org/wiki/Free-rider_problem" target="_blank">the free rider problem.</a>
                  The more patrons one has, the more likely it is that one will distribute the rewards to people who are not contributing.
                  This disincentivizes people from signing up for an artist's Patreon, as they can get the art for free.
                </p>
                <p>
                  While solutions exist to deter this behavior-- such as sending takedown notices to hosting sites and
                  threatening legal action, these often create customer relations issues and cost more time and effort
                  than can be recovered, and can never be fully effective, as people may always share files privately.
                  Additionally, offering physical goods and other creative uncopyable rewards is an option, but may not
                  always be practical.
                </p>
                <p>
                  Artconomy does not have this problem, as each commission is tied to a specific seller who pays
                  individually for their pieces. Thankfully one does not need to exclusively use Patreon or Artconomy.
                  Artconomy is able to handle workload management from your Patreon via the use of Placeholder Orders.
                </p>
              </v-card-text>
            </v-card>
          </v-expansion-panel-content>
          <v-expansion-panel-content>
            <div slot="header"><strong>Is Artconomy Secure?</strong></div>
            <v-card>
              <v-card-text>
                <p>
                  No system is completely secure, and anyone who advises you otherwise should be regarded with
                  suspicion, or at least considered ignorant.
                </p>
                <p>
                  However, Artconomy takes security seriously. We do not allow unencrypted connections to our site.
                  Payment information is stored only as long as required to store it offsite in secure data stores so that
                  even if we are hacked, hackers will have limited ability to steal your information.
                </p>
                <p>
                  Passwords are not stored in plain text, but are hashed to prevent release of your raw password.
                  They are also salted to reduce the probability of hackers finding a password that works with the
                  resulting hash and using it to log into other services.
                </p>
                <p>
                  Artconomy also uses strict frameworks for accessing and manipulating its databases to reduce the
                  probability of SQL injections and makes use of anti-clickjacking technology.
                </p>
                <p>
                  These are only some of the things we do to keep your data safe, and we continue to keep security in
                  mind when developing our products. You are always advised to use
                  <router-link
                      v-if="viewer.username"
                      :to="{name: 'Settings', params: {username: viewer.username, tabName: 'credentials', subTabName: 'two-factor'}}">
                    Two-factor authentication, configurable in your settings,
                  </router-link>
                  <span v-else>
                    Two-factor authentication, configurable in your settings,
                  </span>
                  for extra security, Especially if you are an artist!
                </p>
              </v-card-text>
            </v-card>
          </v-expansion-panel-content>
          <v-expansion-panel-content>
            <div slot="header"><strong>How do I get paid?</strong></div>
            <v-card>
              <v-card-text>
                <p>
                  After you have completed your tasks, the money you've earned will be released to your Artconomy
                  account holdings. From here,
                  <router-link
                      v-if="viewer.username"
                      :to="{name: 'Settings', params: {username: viewer.username, tabName: 'payment', subTabName: 'disbursement'}}"
                  >
                    you may submit a withdrawal request.
                  </router-link>
                  <span v-else>
                    you may submit a withdrawal request.
                  </span>
                  Payouts take 1-2 business days to complete. If you're having an issue with your payout, please email
                  support@artconomy.com.
                </p>
              </v-card-text>
            </v-card>
          </v-expansion-panel-content>
          <v-expansion-panel-content>
            <div slot="header"><strong>What is my pending balance?</strong></div>
            <v-card>
              <v-card-text>
                <p>
                  Money from a customer's credit card has to settle from our internal
                  accounts before it can be sent over to your bank. This can take up to two days from the time the customer's card is charged.
                </p>
                <p>
                  If a customer's card is charged and you complete a commission within the same day, you may need to
                  wait another day or two for us to clear the transaction with our bank before you can withdraw.
                  We are exploring ways to reduce this time for people who make quick-turnaround pieces.
                </p>
                <p>
                  Most artists may rarely or never see a pending balance, since we expect most commissions require more
                  than two days from the time a customer's card is charged to completion.
                </p>
                <p>If you think your balance has been left in pending for longer than two days, please contact
                  support@artconomy.com, as this may indicate an issue on our end.
                </p>
              </v-card-text>
            </v-card>
          </v-expansion-panel-content>
          <v-expansion-panel-content>
            <div slot="header"><strong>Does Artconomy Support Cryptocurrency Payments?</strong></div>
            <v-card>
              <v-card-text>
                <p>
                  Not at this time. However we are looking to implement support for Monero and Bitcoin Cash and
                  potentially other cryptocurrencies in the future.
                </p>
              </v-card-text>
            </v-card>
          </v-expansion-panel-content>
          <v-expansion-panel-content>
            <div slot="header"><strong>How do Character Transfers Work?</strong></div>
            <v-card>
              <v-card-text>
                <p>
                  Don't have a character but want one for your own? Have a character design idea that you think someone
                  else would like? Artconomy allows you to buy, sell, or gift characters using our character transfer
                  feature.
                </p>
                <p>
                  Once you've created a character and uploaded any relevant assets, and you have located a person who is
                  willing to buy or receive the character, you can click the settings button under the lower right-hand
                  expanded menu on a character's page. From there, you will find the Transfer button, where you can
                  select a target user and set a price for the transfer.
                </p>
                <p>
                  You may also elect to include any submissions in which the character is the only one tagged.
                  The receiver will be able to accept or reject the offer, receiving control and rights over the
                  character and any submissions attached to it.
                </p>
                <p>
                  <strong>Note:</strong> Characters are a fuzzy concept in Intellectual Property law.
                  Please make sure you have fully read the
                  <router-link :to="{name: 'CharacterTransferAgreement'}">Character Transfer Agreement</router-link>
                  before transferring or agreeing to receive any characters.
                </p>
              </v-card-text>
            </v-card>
          </v-expansion-panel-content>
          <v-expansion-panel-content>
            <div slot="header"><strong>What are Artconomy Portrait and Landscape?</strong></div>
            <v-card>
              <v-card-text>
                <p>
                  Artconomy Portrait and Landscape are paid services that allow you to get more out
                  of your experience with Artconomy.
                </p>
                <p>Artconomy Portrait allows you to receive messages over email and Telegram when your favorite artists are available for commissions.</p>
                <p>Artconomy Landscape includes Artconomy Portrait, and also greatly reduces the fees involved in selling commissions.</p>
                <p>After signing in, see the Upgrade link in the sidebar for more details.</p>
              </v-card-text>
            </v-card>
          </v-expansion-panel-content>
          <v-expansion-panel-content>
            <div slot="header"><strong>Does Artconomy Support Auctions?</strong></div>
            <v-card>
              <v-card-text>
                <p>
                  Artconomy does not presently support auctions but this is high on our priority list.
                  Be on the lookout for auction support soon!
                </p>
              </v-card-text>
            </v-card>
          </v-expansion-panel-content>
          <v-expansion-panel-content>
            <div slot="header"><strong>Does Artconomy Support the Sale of Physical Goods?</strong></div>
            <v-card>
              <v-card-text>
                <p>
                  Artconomy does not presently support the sale of physical goods aside from original
                  pieces made during the commissioning process. However, we are looking into supporting this,
                  as well as print and merchandising services for things like T-shirts and hats.
                </p>
              </v-card-text>
            </v-card>
          </v-expansion-panel-content>
        </v-expansion-panel>
      </v-tab-item>
      <v-tab-item id="tab-other">
        <v-expansion-panel v-model="otherTab">
          <v-expansion-panel-content>
            <div slot="header"><strong>What are the content ratings and what do they mean?</strong></div>
            <v-card>
              <v-card-text>
                <p>
                  Artconomy caters to varying tastes and strives to give its customers the best viewing
                  experience it can. In order to do so, we have instated a handful of 'rating levels'.
                  <router-link
                      :to="{name: 'Settings', params: {username: viewer.username, tabName: 'options'}}"
                      v-if="viewer.username"
                  >
                    Your rating level can be configured in your settings.
                  </router-link>
                  <span v-else>
                    Your rating level can be configured in your settings.
                  </span>
                </p>
                <p>The following rating levels exist:</p>
                <ol>
                  <li>
                    Clean/Safe for Work: Content which can be safely viewed in most workplaces. Pieces with nudity
                    or especially suggestive clothing do not belong in this category. Pieces with violence or
                    potentially offensive messages do not belong in this category, either.
                  </li>
                  <li>
                    Risque/Mature: This is for content which may contain nudity or risque content which is not suitable
                    for work but is not explicitly pornographic belongs here.
                    Mild violence also belongs in this category.
                  </li>
                  <li>
                    Adult Content: This is for content which is explicitly pornographic but unlikely to violate the
                    sensibilities of most viewers of such content. Moderate violence also belongs in this category.
                  </li>
                  <li>
                    Offensive/Disturbing: This is for content which is extreme in some regard, such as fetish artwork
                    that most viewers would find 'squicky' or disturbing or portrayals of extreme violence.
                  </li>
                </ol>
                <p>
                  Users are expected to categorize their pieces in good faith. If users do not properly categorize,
                  pieces may be categorized for them. Repeated failure to properly categorize can
                  result in account suspension.
                </p>
                <p>
                  If you set a maximum content rating higher than the default of Clean/Safe for work, you will have
                  access to the NSFW/SFW toggle button in the menu. Clicking this will quickly make your experience more
                  presentable for a work environment.
                </p>
              </v-card-text>
            </v-card>
          </v-expansion-panel-content>
          <v-expansion-panel-content>
            <div slot="header"><strong>How do I use the Blacklist?</strong></div>
            <v-card>
              <v-card-text>
                <p>
                  Artconomy's rating system is good for course grain categorization of content, but the content of any
                  given work may be less desirable to a viewer even if it might normally be in a rating they are
                  comfortable with.
                </p>
                <p><strong>Enter the Blacklist:</strong>
                  When you encounter content that is against your tastes, check the tags on the work.
                  Once you locate a tag related to the content you find objectionable, you can go to
                  <router-link
                      :to="{name: 'Settings', params: {username: viewer.username, tabName: 'options'}}"
                      v-if="viewer.username"
                  >
                    your settings page
                  </router-link>
                  <span v-else>
                    your settings page
                  </span>
                  and add it to your blacklist. From then on, content with that tag will be filtered out.
                </p>
                <p>
                  Proper tagging is important. Users are expected to tag their artwork and, by default, all pieces can
                  have tags added by other users. Users who disable tagging for their pieces are responsible for their
                  tags and may be subject to disciplinary action if they do not maintain a reasonable list of tags for
                  their pieces, since this may result in disturbing content being shown to users who do not desire it.
                </p>
                <p>
                  Artconomy does not actively police content on the platform, and cannot prevent all disturbing or
                  offensive imagery from being uploaded, especially since pieces may be marked private. We prefer to
                  give each customer the power to customize his or her viewing experience using the rating and blacklist
                  tools.
                </p>
                <p>
                  Artconomy does, however, respond to legal requests to remove unlawful content, and does not permit
                  unlawful content on its platforms.
                </p>
              </v-card-text>
            </v-card>
          </v-expansion-panel-content>
          <v-expansion-panel-content>
            <div slot="header"><strong>How does watching work?</strong></div>
            <v-card>
              <v-card-text>
                <p>
                  You can watch artists by going to their profile page and clicking the Watch button on their profile.
                  Watching an artist gives you notifications when they've uploaded new content or when they're
                  streaming, or release new products, among other things.
                </p>
                <p>
                  The 'Who's Open?' link in the menu takes you to a page where you can see all currently open products
                  from artists you are watching.
                </p>
                <p>
                  <router-link
                      v-if="viewer.username"
                      :to="{name: 'Upgrade'}"
                  >
                    Want to know the moment an artist is available for commissions? Artconomy Portrait gives you
                    real time notifications on artist availability!
                  </router-link>
                  <span v-else>
                    Want to know the moment an artist is available for commissions? Artconomy Portrait gives you
                    real time notifications on artist availability!
                  </span>
                </p>
              </v-card-text>
            </v-card>
          </v-expansion-panel-content>
          <v-expansion-panel-content>
            <div slot="header"><strong>How does Blocking work?</strong></div>
            <v-card>
              <v-card-text>
                <p>
                  If you find that someone on Artconomy is harassing you or is otherwise not someone whose content you
                  wish to see, you may block them by clicking on the 'block' button on their profile page. Blocking does
                  not remove all content from a user, since some information may be contextually important
                  (such as comments not made directly in response to yours), however it should block most interactions.
                </p>
                <p>
                  If you find a bug in the blocking that allows users to continue harassing you, or you have continued
                  to be harassed on the platform after asking someone to stop, please contact support@artconomy.com with
                  the details. Harassment can be subject to disciplinary action, including account closure, depending on
                  severity.
                </p>
              </v-card-text>
            </v-card>
          </v-expansion-panel-content>
        </v-expansion-panel>
      </v-tab-item>
    </v-tabs-items>
  </v-container>
</template>
<script>
  import {paramHandleArray, paramHandleMap} from '../lib'

  const about = ['what-is-artconomy', 'cost', 'team']
  const buySell = [
    'how-to-buy', 'how-to-sell', 'disputes', 'bank-accounts',
    'workload-management', 'placeholder-orders', 'order-tokens',
    'why-commissions-disabled',
    'why-not-paypal', 'patreon-comparison', 'security',
    'payouts', 'pending-balance', 'crypto-currencies', 'character-transfer',
    'portrait-and-landscape', 'auctions',
    'physical-goods'
  ]
  const other = [
    'content-ratings', 'blacklist', 'watching', 'blocking'
  ]

  export default {
    name: 'FAQ',
    computed: {
      tab: paramHandleMap('tabName', ['subTabName']),
      aboutTab: paramHandleArray('subTabName', about),
      buySellTab: paramHandleArray('subTabName', buySell),
      otherTab: paramHandleArray('subTabName', other)
    }
  }
</script>