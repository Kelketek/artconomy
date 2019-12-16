<template>
  <v-expansion-panels v-model="tab">
    <v-expansion-panel>
      <v-expansion-panel-header>
        <strong>How do I buy commissions on Artconomy?</strong>
      </v-expansion-panel-header>
      <v-expansion-panel-content>
        <v-card>
          <v-card-text>
            <p>
              To buy a commission on Artconomy, find any artist who is open.
              <span @click.capture.stop.prevent="searchOpen" class="who-is-open-link">
                <router-link
                :to="{name: 'SearchProducts'}"
              >
              You can see a list of open artists here!
              </router-link></span>
            </p>
            <p>
              Once you have found a product that you like, click the Order button on the product page and
              fill out the provided form. If you're registered with us, you can even attach your own character
              references with our character profiles feature!
            </p>
            <p>
              The artist will then review your request, ask any questions or make comments, and then will finalize
              the price if they are willing to complete the piece or reject the order if they are not.
            </p>
            <p>
              Once the artist has approved your request, you will be able to pay for the order. If the product is
              protected by
              <router-link
                  :to="{name: 'BuyAndSell', params: {question: 'shield'}}"
              >
                Artconomy Shield</router-link>
              we will hold onto
              the money until the artist completes the work. Otherwise, the artist will arrange with you how to pay
              them.
              They may upload revisions for your approval. Please provide comments to the artist when revisions are
              uploaded to ensure the result is what you are hoping for.
            </p>
            <p>
              Once the artist has completed the work, two things may happen:
            </p>
            <ul>
              <li>If using
                <router-link
                    :to="{name: 'BuyAndSell', params: {question: 'shield'}}"
                >
                  Artconomy Shield</router-link>,
                you may approve the final piece, and the artist will be paid.
              </li>
              <li>Otherwise, the order will then be finalized.</li>
            </ul>
            <p>
              Then you can rate your artist, and if you have an account, you can add it to your collection.
            </p>
          </v-card-text>
        </v-card>
      </v-expansion-panel-content>
    </v-expansion-panel>
    <v-expansion-panel>
      <v-expansion-panel-header>
        <strong>How do I sell commissions on Artconomy?</strong>
      </v-expansion-panel-header>
      <v-expansion-panel-content>
        <v-card>
          <v-card-text>
            <p>
              To sell commissions on Artconomy, you must first
              <router-link
                  :to="{name: 'Options', params: {username: viewer.username}}"
                  v-if="isRegistered"
              >
                enable artist mode in your settings</router-link>
              <span v-else>enable artist mode in your settings</span> so that you can list products.
            </p>
            <p>
              Once artist mode is enabled, you can
              <router-link :to="{name: 'Store', params: {username: viewer.username}}"
                           v-if="isRegistered"
              >go to your store</router-link><span v-else>go to your store</span>,
              where you can configure
              <router-link
                  :to="{name: 'BuyAndSell', params: {question: 'shield'}}"
              >
                Artconomy Shield
              </router-link>
              . Please see the question below about bank accounts. If you cannot link a
              US Bank account, you can opt out of
              <router-link
                  :to="{name: 'BuyAndSell', params: {question: 'shield'}}"
              >
                Artconomy Shield</router-link>, but you will not have access to its protections and features, and your
              products will be marked to alert users that
              <router-link
                  :to="{name: 'BuyAndSell', params: {question: 'shield'}}"
              >
                Artconomy Shield</router-link>
              is not available.
            </p>
            <p>
              After you have created a product, it will be listed on your profile page and on the recently created
              products list on the front page. Buyers may then commission you by clicking on it.
            </p>
            <p>
              Once you have an order, review the commissioner's request and make sure you understand it fully.
              If you are satisfied you understand the commissioner's requirements and wish to take on the work,
              <strong>add any price adjustments necessary</strong>, such as those for shipping the original if you
              include that with your product, or <strong>any extra work that their request requires, like
              wings or backgrounds.</strong>
              Finally, hit the approve button.
            </p>
            <p>
              The commissioner will then review the offer and pay for it if they find it acceptable. If you are not
              using
              <router-link
                  :to="{name: 'BuyAndSell', params: {question: 'shield'}}"
              >
                Artconomy Shield</router-link>, you will need to arrange payment with the customer manually.
              You should then begin the work as soon as you are able, uploading any revisions along the way. When
              you are finished, submit your final piece.
            </p>
            <p>
              The commissioner will then review and approve your work. Once approved, you will receive the money
              that has been held for you. You will then be able to rate your customer and provide comments.</p>
          </v-card-text>
        </v-card>
      </v-expansion-panel-content>
    </v-expansion-panel>
    <v-expansion-panel>
      <v-expansion-panel-header>
        <strong>What is Artconomy Shield?</strong>
      </v-expansion-panel-header>
      <v-expansion-panel-content>
        <v-card>
          <v-card-text>
            <p>
              <em><strong>Artconomy Shield</strong></em> is your protector against the uncertainties of
              commissioning art online!
            </p>
            <p>
              Products protected by Artconomy shield are guaranteed to be completed by the artist, and to be paid
              for by the commissioner. If there's an issue with a piece being commissioned, the commissioner may
              file a
              <router-link
                  :to="{name: 'BuyAndSell', params: { question: 'disputes'}}"
              >dispute
              </router-link>
              for mediation.
            </p>
            <p>
              When you purchase a product with Artconomy shield, we hold onto your payment until the artist
              completes the work. <em><strong>If the artist does not complete the work, you receive your money back,
              minus the shield fee.</strong></em>
            </p>
            <p>
              When, as an artist, you list a product with Artconomy shield, you know the commissioner has already
              paid with their credit card and that they've agreed to our dispute resolution service.
              Unless a
              <router-link
                  :to="{name: 'BuyAndSell', params: {question: 'disputes'}}"
              >dispute
              </router-link>
              is found in favor of your commissioner, <em><strong>your money will be deposited in your bank account
              once the
              commission is completed.</strong></em>
            </p>
            <p>
              Artists and commissioners who use Artconomy Shield help build trust in the artistic community.
              Artists who are unable to use Artconomy Shield (such as those without US Bank Accounts) can still
              list products and take orders on Artconomy, but must arrange payment with commissioners manually.
            </p>
            <p>
              Orders made without Artconomy Shield may also have ads on the product, profile, and order pages
              to help pay for the cost of providing Artconomy's service.
            </p>
            <p>Artists using Shield will be assessed a one-time setup fee, required by our payment processor, of
              <strong>$1.00</strong>.
              This fee is not assessed until the artist has earned at least $1 through sales, and is non-refundable.
            </p>
            <p v-if="pricing.x">
              Artconomy's fees for
              <router-link
                  :to="{name: 'BuyAndSell', params: {question: 'shield'}}"
              >
                Artconomy Shield
              </router-link>
              are {{pricing.x.standard_percentage}}% + ${{pricing.x.standard_static}} for
              each order.
            </p>
            <p v-if="pricing.x">
              Artists using
              <router-link
                  :to="{name: 'BuyAndSell', params: {question: 'portrait-and-landscape'}}"
              >Artconomy Landscape
              </router-link>
              receive a bonus amount of
              {{bonusPercentage}}% + ${{pricing.x.premium_static_bonus}} on each commission!
            </p>
            <p>
              <em><strong>
                Commissioning artists or taking orders without Artconomy Shield is done at your own risk, and
                Artconomy provides no guarantees for unshielded orders.</strong>
              </em>
            </p>
            <p>Look for the shield icon on products to see if they're shielded!</p>
            <p>
              <v-icon class="green--text">fa-shield</v-icon>
            </p>
          </v-card-text>
        </v-card>
      </v-expansion-panel-content>
    </v-expansion-panel>
    <v-expansion-panel>
      <v-expansion-panel-header>
        <strong>How are disputes handled?</strong>
      </v-expansion-panel-header>
      <v-expansion-panel-content>
        <v-card>
          <v-card-text>
            <p>
              When a commission with
              <router-link
                  :to="{name: 'BuyAndSell', params: {question: 'shield'}}"
              >
                Artconomy Shield
              </router-link>
              is finished, or an extended period between the task's acceptance and its
              completion has elapsed, a commissioner will have the option to file a dispute. Disputes will come up
              for review by our staff.
            </p>
            <p>
              Disputes are evaluated on a case-by-case basis. Our staff will review the order's history, and ask any
              additional questions, or give opportunities for action as needed before making any decisions.
            </p>
            <p>One or more of the following conditions will make an order eligible for a refund:</p>
            <ul>
              <li>The artist has taken an extraordinary amount of time beyond estimate to complete the work (this
                will not be considered if the final is already delivered by the time the dispute is filed)
              </li>
              <li>The artist has drawn something <strong>severely</strong> under their standard quality of work as
                depicted in their gallery.
              </li>
              <li>The artist has drawn something completely different than what a reasonable reader would have
                expected the commission notes to require.
              </li>
              <li>Sales involving original goods being shipped do not arrive or are damaged. Recipient must provide
                proof of damage. Artists are expected to use trackable forms of shipment and buy insurance to cover
                damage so that they may claim the difference from their carrier.
              </li>
            </ul>
            <p>The following conditions will <strong>NOT</strong> make an order eligible for a refund:</p>
            <ul>
              <li>The artist is moderately over estimate.</li>
              <li>The final piece has flaws which were in previously posted revisions that were either commented on
                by the commissioner or which the commissioner had time for comment and no comment was made.
              </li>
              <li>The piece is within reasonable variance of the artist's history of quality, but it is not quite
                what the commissioner hoped for.
              </li>
              <li>The final piece has minor differences from the description, or differences that could result from
                reasonable mistakes when reading the commission notes.
              </li>
            </ul>
            <p>
              The above cases, while regrettable, will not be warranted against by Artconomy for the cost of the
              commission price. The commissioner is free to include any information about their commissioning
              experience when rating the artist.
            </p>
            <p>
              <strong>Products without Artconomy Shield do not have dispute resolution services available.</strong>
            </p>
          </v-card-text>
        </v-card>
      </v-expansion-panel-content>
    </v-expansion-panel>
    <v-expansion-panel>
      <v-expansion-panel-header>
        <strong>What are Artconomy Portrait and Landscape?</strong>
      </v-expansion-panel-header>
      <v-expansion-panel-content>
        <v-card>
          <v-card-text>
            <p>
              Artconomy Portrait and Landscape are paid services that allow you to get more out
              of your experience with Artconomy.
            </p>
            <p>Artconomy Portrait allows you to <strong>receive messages over email and Telegram when your favorite
              artists are available</strong> for commissions.</p>
            <p>Artconomy Landscape includes Artconomy Portrait, and also gives artists a bonus on each commission sale!</p>
            <p v-if="pricing.x">
              Artconomy's fees for
              <router-link
                  :to="{name: 'BuyAndSell', params: {question: 'shield'}}"
              >
                Artconomy Shield
              </router-link>
              are {{pricing.x.standard_percentage}}% + ${{pricing.x.standard_static}} for
              each order.
            </p>
            <p v-if="pricing.x">
              When using landscape, artists receive an additional bonus of
              <strong>{{bonusPercentage}}% + ${{pricing.x.premium_static_bonus}}!</strong>
            </p>
            <router-link v-if="isRegistered" :to="{name: 'Upgrade'}">Click this link for more details!
            </router-link>
            <p v-else>Click the Upgrade link in the sidebar after you're logged in to upgrade your account!</p>
          </v-card-text>
        </v-card>
      </v-expansion-panel-content>
    </v-expansion-panel>
    <v-expansion-panel>
      <v-expansion-panel-header>
        <strong>What banks can be linked to Artconomy Shield?</strong>
      </v-expansion-panel-header>
      <v-expansion-panel-content>
        <v-card>
          <v-card-text>
            <p>
              At present, only US Bank accounts can be integrated with Artconomy. We are looking into ways to
              support European and other banks but do not currently have a method of doing so. Artists must have a
              bank
              linked to use
              <router-link
                  :to="{name: 'BuyAndSell', params: {question: 'shield'}}"
              >Artconomy Shield.
              </router-link>
              However, Artconomy Shield is not required to list products and take orders on Artconomy.
            </p>
          </v-card-text>
        </v-card>
      </v-expansion-panel-content>
    </v-expansion-panel>
    <v-expansion-panel>
      <v-expansion-panel-header>
        <strong>What is AWOO and how can it help me manage my workload?</strong>
      </v-expansion-panel-header>
      <v-expansion-panel-content>
        <v-card>
          <v-card-text>
            <p>
              Artconomy understand the problems artists have with managing their workload and communicating with
              commissioners. That's why we created Artconomy Workload Organization and Overview (AWOO).
            </p>
            <p>
              AWOO begins with your
              <router-link
                  :to="{name: 'BuyAndSell', params: {questions: 'options'}}"
                  v-if="isRegistered"
              >Slots, configurable in your settings.
              </router-link>
              <span v-else>
                      Slots, configurable in your settings.
                    </span>
              Your slots are the number of open spaces you have for commissions. Most commissions should take up one slot,
              but if you offer a product that takes more time, you can change the number of slots it takes up.
              For instance, if you have 10 slots, and sell inked pieces that take up 2 slots each, Artconomy will close
              commissions once you have five of them.
            </p>
            <p>
              AWOO is able to track multiple products' slots. If you set your slots to 10, and sell full color pieces
              that take up five slots, you could have one full color commission and two inked pieces (totalling 9 points)
              leaving you with one point remaining. If you don't have any products that take up only one point,
              AWOO will close commissions for you.
            </p>
            <p>
              In addition to this, you may also specify the 'Max at Once' setting for a product. If you never want
              to do more than two sketches at a time, you would set this to 2 for your sketch product.
              This will make sure that if you already have two sketches accepted, AWOO will delist sketches from your
              store so you don't receive more requests for them.
            </p>
            <p>
              AWOO manages when you are considered 'open' for commissions, sending real-time alerts to Portrait and
              Landscape subscribers when you are available. Note that you may still be closed for commissions even
              if you have some workload to spare. See
              <router-link
                  :to="{name: 'BuyAndSell', params: {question: 'why-commissions-disabled'}}"
              >
                'Why are my Commissions Disabled?'
              </router-link>
              for more information as to why this may happen.
            </p>
            <p>You can effectively disable AWOO's slot management by setting your Slot count to a number
              so high you'll never reach it. You can then open and close yourself with the
              <router-link
                  :to="{name: 'Settings', params: {username: viewer.username, tabName: 'options'}}"
                  v-if="isRegistered"
              >Commissions Closed setting.
              </router-link>
              <span v-else>
                      Commissions Closed setting, available on your settings page.
                    </span>
              <strong>This is not recommended unless you are experienced in managing
                your workload.</strong> Appearing to be open when you are not leads to customer service issues,
              which can affect your rating and reputation. If you feel that you need more slots than the maximum setting,
              <a href="#" @click.prevent="setSupport(true)">please contact support</a>.
            </p>
            <p>
              <strong>All orders offer a direct communication line with your commissioner.</strong>
              Commenting on an order sends an email alert and notification to the commissioner for them to review.
              This ensures that you do not have to keep individual track of customers' email addresses to get a
              hold of them, and you never have to write a journal entry with the subject 'if I owe you art, message me.'
              Feel free to comment and ask questions to make sure you can give your customers the best
              experience possible!
            </p>
          </v-card-text>
        </v-card>
      </v-expansion-panel-content>
    </v-expansion-panel>
    <v-expansion-panel>
      <v-expansion-panel-header>
        <strong>How can I invoice customers, or track orders not made on the site?</strong>
      </v-expansion-panel-header>
      <v-expansion-panel-content>
        <v-card>
          <v-card-text>
            <p>
              If you're out and about at a convention, working on a special project, or you're taking orders on the fly
              from customers in your stream, you might want to create an order for tracking yourself,
              instead of having a customer do it.
              <router-link
                  :to="{name: 'BuyAndSell', params: {question: 'awoo-workload-management'}}">
                AWOO
              </router-link>
              can help you keep track of these orders. You can create a new invoice from your
              <router-link :to="{name: 'Sales', params: {username: viewer.username}}"
                           v-if="isRegistered && viewer.artist_mode"
              >sales page</router-link><span v-else>sales page</span>. Just click the green button in the lower right to
              get started!
            </p>
            <p>Invoices can do several neat things. For instance:</p>
            <ul>
              <li>You can specify an email or Artconomy user name to send the invoice to in order to collect payment.</li>
              <li>You can use your existing product listings as a template for pricing and workload management.</li>
              <li>You can prevent AWOO from tracking any impact on your workload if the piece is already finished, and
                you just need to collect payment or send the finished piece.</li>
              <li>You can handle tasks that have already been paid, but which impact your workload, so
                AWOO can keep track of them.</li>
              <li>You can issue a completely custom order not related to any product you currently have listed.</li>
              <li>You can create an order that doesn't have the customer's information-- useful if you want to track the
                impact of an outside project or commission but don't need to send updates to anyone.</li>
            </ul>
            <p>
              Invoices can always be issued, regardless of whether or not your commissions are closed, or a product is
              normally unavailable. <strong>Please be cautious when taking orders this way if you already have a full workload--</strong>
              failing to deliver pieces in a timely manner can affect your reputation, and it is better to keep promises
              you have already made than to make new ones.
            </p>
          </v-card-text>
        </v-card>
      </v-expansion-panel-content>
    </v-expansion-panel>
    <v-expansion-panel>
      <v-expansion-panel-header>
        <strong>Why are my commissions disabled?</strong>
      </v-expansion-panel-header>
      <v-expansion-panel-content>
        <v-card>
          <v-card-text>
            <p>
              <router-link
                  :to="{name: 'BuyAndSell', params: {question: 'awoo-workload-management'}}">
                AWOO
              </router-link>
              uses a smart algorithm to help determine if you should be considered open for commissions.
              On your sales page, you will see information about your current commission status and any reasons
              why you may not be open. Some of these reasons may include:
            </p>
            <ul>
              <li>You have marked yourself as 'commissions closed' in your settings.</li>
              <li>You have used up all of your slots, also configurable in your settings.</li>
              <li>You still have some slots, but none of your products will fit in the remaining workload.
              </li>
              <li>You still have some slots, but any products which DO fit in the remaining ones have
                already reached their 'max at once' limit.
              </li>
              <li>
                You still have some slots, do not have commissions closed, and have viable products,
                but you still have open requests left over from the last time you were open for commissions. You
                must accept or reject these before you will be able to take new orders, in order to reduce the
                incidence of customer service issues.
              </li>
            </ul>
          </v-card-text>
        </v-card>
      </v-expansion-panel-content>
    </v-expansion-panel>
    <v-expansion-panel>
      <v-expansion-panel-header>
        <strong>Why not use PayPal?</strong>
      </v-expansion-panel-header>
      <v-expansion-panel-content>
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
              <li>PayPal has a mixed reputation when dealing with adult content. Their written policy, taken literally,
                bans all adult content, though many still use it for the purpose.
              </li>
            </ul>
            <p>
              <router-link
                  :to="{name: 'BuyAndSell', params: {question: 'shield'}}"
              >
                Artconomy Shield
              </router-link>
              is built with the needs of commissioners and artists in mind, and specializes in the needs of both.
              PayPal's limitations also prevent it from being a backend for Artconomy to take payments, so we are
              unable to accept payments via PayPal.
            </p>
            <p>
              Artists not using
              <router-link
                  :to="{name: 'BuyAndSell', params: {question: 'shield'}}"
              >Artconomy Shield
              </router-link>
              may elect to accept payment using PayPal, but will not be
              protected by our verification and dispute resolution.
            </p>
          </v-card-text>
        </v-card>
      </v-expansion-panel-content>
    </v-expansion-panel>
    <v-expansion-panel>
      <v-expansion-panel-content>
        <v-expansion-panel-header>
          <strong>How does Artconomy compare to Patreon?</strong>
        </v-expansion-panel-header>
        <v-card>
          <v-card-text>
            <p>
              Patreon is a popular platform for artists that allows them to receive monthly
              contributions from patrons. Patrons are also able to receive exclusive rewards for being monthly
              donors.
            </p>
            <p>
              We believe that services like Patreon and Artconomy are best used together to help artists achieve their goals of
              self-sufficiency from their artistic work.
            </p>
            <p>
              Patreon has a significant limitation however--
              <a href="https://en.wikipedia.org/wiki/Free-rider_problem" target="_blank">the free rider problem.</a>
              The more patrons one has, the more likely it is that one will distribute the rewards to people who are
              not contributing.
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
            </p>
            <p>Artconomy may add functionality like Patreon has in the future, but for now remains focused on building the
              best freelance art business toolkit.</p>
          </v-card-text>
        </v-card>
      </v-expansion-panel-content>
    </v-expansion-panel>
    <v-expansion-panel>
      <v-expansion-panel-header>
        <strong>What are Featured Products?</strong>
      </v-expansion-panel-header>
      <v-expansion-panel-content>
        <v-card>
          <v-card-text>
            <p>
              Featured products are products hand-curated by Artconomy staff.
              Several criteria are used to determine whether a product is featured,
              <em>some of which are subjective and up to staff judgement.</em>
              These include (but are not limited to):
            </p>
            <ul>
              <li>Quality of the work Offered</li>
              <li>Ratings and feedback from commissioners who have worked with the artist</li>
              <li>Value for price</li>
              <li>Shield Capability (Not required, but it helps!)</li>
            </ul>
            <p>
              Featured products may change and are rotated on the front page at random. If you believe there is a
              product that should be considered for featured status,
              <a href="#" @click.prevent="setSupport(true)">please contact support</a>.
            </p>
          </v-card-text>
        </v-card>
      </v-expansion-panel-content>
    </v-expansion-panel>
    <v-expansion-panel>
      <v-expansion-panel-header>
        <strong>Is Artconomy Secure?</strong>
      </v-expansion-panel-header>
      <v-expansion-panel-content>
        <v-card>
          <v-card-text>
            <p>
              No system is completely secure, and anyone who advises you otherwise should be regarded with
              suspicion, or at least considered ignorant.
            </p>
            <p>
              However, Artconomy takes security seriously. We do not allow unencrypted connections to our site.
              Payment information is handled only long enough to process it and to store it offsite in secure data
              stores so that even if we are hacked, hackers will have limited ability to steal your information.
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
              For especially sensitive data that must be stored on our servers (such as tax ID information), we use
              encryption with offline, cold stored, secured keys, which are used only as long as explicit operations
              by our executive technical staff require.
            </p>
            <p>
              These are only some of the things we do to keep your data safe, and we continue to keep security in
              mind when developing our products. You are always advised to use
              <router-link
                  v-if="isRegistered"
                  :to="{name: 'Settings', params: {username: viewer.username, tabName: 'credentials', subTabName: 'two-factor'}}">
                Two-factor authentication, configurable in your settings,
              </router-link>
              <span v-else>
                      Two-factor authentication, configurable in your settings,
                    </span>
              for extra security, Especially if you are an artist!
            </p>
            <p>Do not share your account password with anyone. Artconomy staff will <em><strong>never</strong></em>
              ask for your password.</p>
          </v-card-text>
        </v-card>
      </v-expansion-panel-content>
    </v-expansion-panel>
    <v-expansion-panel>
      <v-expansion-panel-content>
        <v-expansion-panel-header>
          <strong>How do I get paid?</strong>
        </v-expansion-panel-header>
        <v-card>
          <v-card-text>
            <p>
              After you have completed your tasks, the money you've earned will be released to your Artconomy
              account holdings. It will automatically be sent to your bank account, unless you have opted out of
              auto withdraw, in which case
              <router-link
                  v-if="isRegistered"
                  :to="{name: 'Settings', params: {username: viewer.username, tabName: 'payment', subTabName: 'disbursement'}}"
              >
                you may submit a withdrawal request.
              </router-link>
              <span v-else>
                      you may submit a withdrawal request.
                    </span>
              Payouts take up to 5 business days to complete. If you're having an issue with your payout,
              <a href="#" @click.prevent="setSupport(true)">please contact support!</a>
            </p>
          </v-card-text>
        </v-card>
      </v-expansion-panel-content>
    </v-expansion-panel>
    <v-expansion-panel>
      <v-expansion-panel-header>
        <strong>Does Artconomy Support Cryptocurrency Payments?</strong>
      </v-expansion-panel-header>
      <v-expansion-panel-content>
        <v-card>
          <v-card-text>
            <p>
              Not at this time. However we are looking to implement support for Monero
              and potentially other cryptocurrencies in the future.
            </p>
          </v-card-text>
        </v-card>
      </v-expansion-panel-content>
    </v-expansion-panel>
    <v-expansion-panel>
      <v-expansion-panel-header>
        <strong>Does Artconomy Support Auctions?</strong>
      </v-expansion-panel-header>
      <v-expansion-panel-content>
        <v-card>
          <v-card-text>
            <p>
              Artconomy does not presently support auctions but may do so in the future.
            </p>
          </v-card-text>
        </v-card>
      </v-expansion-panel-content>
    </v-expansion-panel>
    <v-expansion-panel>
      <v-expansion-panel-header><strong>Does Artconomy Support the Sale of Physical Goods?</strong></v-expansion-panel-header>
      <v-expansion-panel-content>
        <v-card>
          <v-card-text>
            <p>
              Artconomy does not presently support the sale of physical goods aside from original
              pieces made during the commissioning process-- it does not have an inventory system.
              However, we are looking into supporting this, as well as print and merchandising services for things
              like T-shirts and hats.
            </p>
          </v-card-text>
        </v-card>
      </v-expansion-panel-content>
    </v-expansion-panel>
  </v-expansion-panels>
</template>

<script lang="ts">
import Component, {mixins} from 'vue-class-component'
import Viewer from '@/mixins/viewer'
import {paramHandleArray} from '@/lib'
import QuestionSet from '@/components/views/faq/mixins/question-set'
import {FormController} from '@/store/forms/form-controller'

const buySell = [
  'how-to-buy', 'how-to-sell', 'shield', 'disputes', 'portrait-and-landscape',
  'bank-accounts',
  'awoo-workload-management', 'outside-orders',
  'why-commissions-disabled',
  'why-not-paypal', 'patreon-comparison', 'featured-products', 'security',
  'payouts', 'crypto-currencies',
  'auctions', 'physical-goods',
]
  @Component
export default class BuyAndSell extends mixins(Viewer, QuestionSet) {
    public searchForm: FormController = null as unknown as FormController
    @paramHandleArray('question', buySell)
    public tab!: number

    public get bonusPercentage() {
      /* istanbul ignore if */
      if (!this.pricing.x) {
        return NaN
      }
      return this.pricing.x.standard_percentage * (this.pricing.x.premium_percentage_bonus / 100)
    }
    public searchOpen() {
      this.searchForm.reset()
      this.$router.push({name: 'SearchProducts'})
    }
    public created() {
      this.searchForm = this.$getForm('search')
    }
}
</script>
