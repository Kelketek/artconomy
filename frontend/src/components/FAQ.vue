<template>
  <v-container>
    <v-tabs v-model="tab" fixed-tabs>
      <v-tab href="#tab-about">
        About
      </v-tab>
      <v-tab href="#tab-second">
        Buying/Selling
      </v-tab>
    </v-tabs>
    <v-tabs-items v-model="tab">
      <v-tab-item id="tab-about">
        <v-expansion-panel v-model="aboutTab">
          <v-expansion-panel-content>
            <div slot="header"><strong>What is Artconomy</strong></div>
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
                <h3>CEO and Lead Developer: Fox Piacenti</h3>
                <p>Fox Piacenti is a long term online role player who has had a passion to see characters
                  come alive online. He has worked as a lead developer, administrator, and director in the recreational
                  and professional spheres.</p>
                <p>Fox began work on Artconomy upon observing the difficulties encountered when commissioning online, and
                  realizing that he rarely commissioned in person but frequently did at creative conventions,
                  where one could meet face-to-face with artists. He wanted to create a service where it was as easy
                  to commission online as it was in person.</p>
                <h3>Marketing Director: Eris Griffon</h3>
              </v-card-text>
            </v-card>
          </v-expansion-panel-content>
        </v-expansion-panel>
      </v-tab-item>
      <v-tab-item id="tab-second">
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
                <p>At present, only US Bank accounts can be integrated with Artconomy. We are looking into ways to
                  support European and other banks but do not currently have a method of doing so.
                </p>
              </v-card-text>
            </v-card>
          </v-expansion-panel-content>
          <v-expansion-panel-content>
            <div slot="header"><strong>How can I manage my workload with Artconomy's tools?</strong></div>
            <v-card>
              <v-card-text>
              </v-card-text>
            </v-card>
          </v-expansion-panel-content>
          <v-expansion-panel-content>
            <div slot="header"><strong>What are placeholder orders?</strong></div>
            <v-card>
              <v-card-text>
              </v-card-text>
            </v-card>
          </v-expansion-panel-content>
          <v-expansion-panel-content>
            <div slot="header"><strong>What are order tokens?</strong></div>
            <v-card>
              <v-card-text>
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
                  <li>PayPal's dispute resolution is limited and not well suited for art, especially when using their personal service.</li>
                  <li>PayPal has been known to suspend accounts with little recourse or comment.</li>
                  <li>PayPal has a strict policy against mature content. Artists found taking payment for mature commissions may find their accounts abruptly closed.</li>
                </ul>
                <p>Artconomy is built with the needs of commissioners and artists in mind, and specializes in the needs of both.</p>
              </v-card-text>
            </v-card>
          </v-expansion-panel-content>
          <v-expansion-panel-content>
            <div slot="header"><strong>How does Artconomy compare to Patreon?</strong></div>
            <v-card>
              <v-card-text>
              </v-card-text>
            </v-card>
          </v-expansion-panel-content>
          <v-expansion-panel-content>
            <div slot="header"><strong>Is Artconomy Secure?</strong></div>
            <v-card>
              <v-card-text>
              </v-card-text>
            </v-card>
          </v-expansion-panel-content>
          <v-expansion-panel-content>
            <div slot="header"><strong>Does Artconomy Support Cryptocurrency Payments?</strong></div>
            <v-card>
              <v-card-text>
              </v-card-text>
            </v-card>
          </v-expansion-panel-content>
        </v-expansion-panel>
        <v-expansion-panel-content>
          <div slot="header"><strong>How do Character Transfers Work?</strong></div>
          <v-card>
            <v-card-text>
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
    'why-not-paypal', 'patreon-comparison', 'security',
    'crypto-currencies', 'character-transfer',
    'portrait-and-landscape', 'auctions',
    'physical-goods'
  ]

  export default {
    name: 'FAQ',
    computed: {
      tab: paramHandleMap('tabName', ['subTabName']),
      aboutTab: paramHandleArray('subTabName', about),
      buySellTab: paramHandleArray('subTabName', buySell)
    }
  }
</script>