<template>
  <v-expansion-panels v-model="tab">
    <ac-question>
      <template #title> How do I buy commissions on Artconomy? </template>
      <template #default>
        <v-card-text>
          <iframe
            :width="videoWidth"
            :height="videoHeight"
            src="https://www.youtube-nocookie.com/embed/1PyT9JgcDDo?si=Nsp7eYiCS9h3-KmX"
            title="YouTube video player"
            allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
            allowfullscreen
          />
          <p>
            To buy a commission on Artconomy, find any artist who is open.
            <span
              class="who-is-open-link"
              @click.capture.stop.prevent="searchOpen"
            >
              <router-link :to="{ name: 'SearchProducts' }">
                You can see a list of open artists here!
              </router-link></span
            >
          </p>
          <p>
            Once you have found a product that you like, click the Order button
            on the product page and fill out the provided form. If you're
            registered with us, you can even attach your own character
            references with our character profiles feature! Even if you're not,
            you can still upload reference images to your order.
          </p>
          <p>
            The artist will then review your request, ask any questions or make
            comments, and then will finalize the price if they are willing to
            complete the piece or reject the order if they are not.
          </p>
          <p>
            Once the artist has approved your request, you will be able to pay
            for the order. If the product is protected by
            <router-link
              :to="{ name: 'BuyAndSell', params: { question: 'shield' } }"
            >
              Artconomy Shield
            </router-link>
            we will hold onto the money until the artist completes the work.
            Otherwise, the artist will arrange with you how to pay them. They
            may upload revisions for your approval. Please provide comments to
            the artist when revisions are uploaded to ensure the result is what
            you are hoping for.
          </p>
          <p>Once the artist has completed the work, two things may happen:</p>
          <ul>
            <li>
              If using
              <router-link
                :to="{ name: 'BuyAndSell', params: { question: 'shield' } }"
              >
                Artconomy Shield
              </router-link>
              , you may approve the final piece or dispute it. If you do
              neither, it will be auto-approved in a few days.
            </li>
            <li>Otherwise, the order will then be finalized.</li>
          </ul>
          <p>
            Then you can rate your artist, and if you have an account, you can
            add it to your collection.
          </p>
        </v-card-text>
      </template>
    </ac-question>
    <ac-question>
      <template #title> How do I sell commissions on Artconomy? </template>
      <template #default>
        <v-card-text>
          <iframe
            :width="videoWidth"
            :height="videoHeight"
            src="https://www.youtube-nocookie.com/embed/1PyT9JgcDDo?si=Nsp7eYiCS9h3-KmX"
            title="YouTube video player"
            allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
            allowfullscreen
          />
          <p>
            To sell commissions on Artconomy, you must first
            <router-link
              v-if="isRegistered"
              :to="{ name: 'Options', params: { username: viewer!.username } }"
            >
              enable artist mode in your settings
            </router-link>
            <span v-else>enable artist mode in your settings</span> so that you
            can list products.
          </p>
          <p>
            Once artist mode is enabled, you can
            <router-link
              v-if="isRegistered"
              :to="{ name: 'Store', params: { username: viewer!.username } }"
            >
              go to your store
            </router-link>
            <span v-else>go to your store</span>, where you can configure (or
            opt out of) the optional
            <router-link
              :to="{ name: 'BuyAndSell', params: { question: 'shield' } }"
            >
              Artconomy Shield
            </router-link>
            escrow service. Please see the question below about
            <router-link
              :to="{
                name: 'BuyAndSell',
                params: { question: 'bank-accounts' },
              }"
            >
              bank accounts
            </router-link>
            to learn about which countries are supported for shield.
          </p>
          <p>
            After you have created a product, it will be listed on your profile
            page and on the recently created products list on the front page.
            Buyers may then commission you by clicking on it.
          </p>
          <p>
            Once you have an order, review the commissioner's request and make
            sure you understand it fully. If you are satisfied you understand
            the commissioner's requirements and wish to take on the work,
            <strong>add any price adjustments necessary</strong>, such as those
            for shipping the original if you include that with your product, or
            <strong
              >any extra work that their request requires, like wings or
              backgrounds.</strong
            >
            Finally, hit the 'Accept' button under the Payment tab.
          </p>
          <p>
            The commissioner will then review the offer and pay for it if they
            find it acceptable. If you are not using
            <router-link
              :to="{ name: 'BuyAndSell', params: { question: 'shield' } }"
            >
              Artconomy Shield
            </router-link>
            , you will need to arrange payment with the customer manually. You
            should then begin the work as soon as you are able, uploading any
            revisions along the way. When you are finished, submit your final
            piece.
          </p>
          <p>
            The commissioner will then review and approve your work. Once
            approved, you will receive the money that has been held for you. You
            will then be able to rate your customer and provide comments.
          </p>
        </v-card-text>
      </template>
    </ac-question>
    <ac-question>
      <template #title> What is Artconomy Shield? </template>
      <template #default>
        <v-card-text>
          <p>
            <em><strong>Artconomy Shield</strong></em> is your protector against
            the uncertainties of commissioning art online!
          </p>
          <p>
            Products protected by Artconomy shield are guaranteed to be
            completed by the artist, and to be paid for by the commissioner. If
            there's an issue with a piece being commissioned, the commissioner
            may file a
            <router-link
              :to="{ name: 'BuyAndSell', params: { question: 'disputes' } }"
            >
              dispute
            </router-link>
            for mediation.
          </p>
          <p>
            When you purchase a product with Artconomy shield, we hold onto your
            payment until the artist completes the work.
            <em
              ><strong
                >If the artist does not complete the work, you receive your
                money back, minus the shield fee.</strong
              ></em
            >
          </p>
          <p>
            When, as an artist, you list a product with Artconomy shield, you
            know the commissioner has already paid with their credit card and
            that they've agreed to our dispute resolution service. Unless a
            <router-link
              :to="{ name: 'BuyAndSell', params: { question: 'disputes' } }"
            >
              dispute
            </router-link>
            is found in favor of your commissioner,
            <em
              ><strong
                >your money will be deposited in your bank account once the
                commission is completed.</strong
              ></em
            >
          </p>
          <p>
            Artists and commissioners who use Artconomy Shield help build trust
            in the artistic community. However, use of Artconomy Shield is
            optional-- you can use whatever payment processor you like.
          </p>
          <p>
            <em
              ><strong>
                Commissioning artists or taking orders without Artconomy Shield
                is done at your own risk, and Artconomy provides no guarantees
                for unshielded orders.</strong
              >
            </em>
          </p>
          <p>
            Look for the shield icon on products to see if they're shielded!
          </p>
          <p>
            <v-icon class="green--text" :icon="mdiShieldHalfFull" />
          </p>
        </v-card-text>
      </template>
    </ac-question>
    <ac-question>
      <template #title> How are disputes handled? </template>
      <template #default>
        <v-card-text>
          <p>
            When a commission with
            <router-link
              :to="{ name: 'BuyAndSell', params: { question: 'shield' } }"
            >
              Artconomy Shield
            </router-link>
            is finished, or an extended period between the task's acceptance and
            its completion has elapsed, a commissioner will have the option to
            file a dispute. Disputes will come up for review by our staff.
          </p>
          <p>
            Disputes are evaluated on a case-by-case basis. Our staff will
            review the order's history, and ask any additional questions, or
            give opportunities for action as needed before making any decisions.
          </p>
          <p>
            One or more of the following conditions will make an order eligible
            for a refund:
          </p>
          <ul>
            <li>
              The artist has taken an extraordinary amount of time beyond
              estimate to complete the work (this will not be considered if the
              final is already delivered by the time the dispute is filed)
            </li>
            <li>
              The artist has drawn something <strong>severely</strong> under
              their standard quality of work as depicted in their gallery.
            </li>
            <li>
              The artist has drawn something completely different than what a
              reasonable reader would have expected the commission notes to
              require.
            </li>
            <li>
              Sales involving original goods being shipped do not arrive or are
              damaged. Recipient must provide proof of damage. Artists are
              expected to use trackable forms of shipment and buy insurance to
              cover damage so that they may claim the difference from their
              carrier.
            </li>
          </ul>
          <p>
            The following conditions will <strong>NOT</strong> make an order
            eligible for a refund:
          </p>
          <ul>
            <li>The artist is moderately over estimate.</li>
            <li>
              The final piece has flaws which were in previously posted
              revisions that were either commented on by the commissioner or
              which the commissioner had time for comment and no comment was
              made.
            </li>
            <li>
              The piece is within reasonable variance of the artist's history of
              quality, but it is not quite what the commissioner hoped for.
            </li>
            <li>
              The final piece has minor differences from the description, or
              differences that could result from reasonable mistakes when
              reading the commission notes.
            </li>
          </ul>
          <p>
            The above cases, while regrettable, will not be warranted against by
            Artconomy for the cost of the commission price. The commissioner is
            free to include any information about their commissioning experience
            when rating the artist.
          </p>
          <p>
            <strong
              >Products without Artconomy Shield do not have dispute resolution
              services available.</strong
            >
          </p>
        </v-card-text>
      </template>
    </ac-question>
    <ac-question>
      <template #title>
        What are the different service plans? Which one is right for me?
      </template>
      <template #default>
        <v-card-text>
          <p>
            Artconomy has three plans to choose from, depending on where you are
            in your professional journey.
          </p>
          <h3>The Free Plan</h3>
          <p>
            The free plan is for people who take commissions on the side or only
            rarely take them. It allows you to track up to one order for free.
            It handles all of the references, the description, communication
            with your commissioner, and provides a place for you to upload
            revisions/WIPs for comment on that order.
          </p>
          <p>
            The free plan is a great way to test if Artconomy is truly
            <strong>right for you and your workflow.</strong>
          </p>
          <p>
            For extra protection on an order, you can enable
            <router-link
              :to="{ name: 'BuyAndSell', params: { question: 'shield' } }"
            >
              Artconomy Shield,
            </router-link>
            our escrow service, or you can use your payment processor of choice
            to handle the payment.
          </p>
          <h3>The Basic Plan</h3>
          <p>
            The basic plan is best for artists who don't have a high volume of
            orders, but are expecting to handle more than one commission a
            month.
          </p>
          <p>
            The basic plan allows you to track as many orders as you like on
            Artconomy. If you use shield on your orders, the only cost will be
            the shield fee. The basic plan comes with a slight discount on the
            shield fee.
          </p>
          <p>
            If you want to track an order without using shield (such as for when
            shield isn't available in your country, or your customer prefers
            PayPal or another processor), you'll be assessed a small fee. At the
            end of your monthly billing cycle, your card will be charged for
            however many orders were tracked without shield.
          </p>
          <h3>Artconomy Landscape</h3>
          <p>
            Artconomy Landscape is our premium offering. In exchange for a
            monthly fee, you get a sharp discount on Artconomy Shield, and you
            can track as many non-shield orders as you like for free!
          </p>
          <p>
            To learn more about
            <router-link
              :to="{ name: 'BuyAndSell', params: { question: 'landscape' } }"
            >
              Landscape,
            </router-link>
            check its main FAQ entry.
          </p>
          <p v-if="isRegistered">
            <router-link
              :to="{ name: 'Upgrade', params: { username: viewerName } }"
            >
              You can upgrade (or downgrade) to your preferred plan here.
            </router-link>
          </p>
          <p v-else>
            Once you're logged in, you can use the "Upgrade" link in the sidebar
            to change your plan.
          </p>
        </v-card-text>
      </template>
    </ac-question>
    <ac-question>
      <template #title> What is Artconomy Landscape? </template>
      <template #default>
        <v-card-text>
          <p>
            Artconomy Landscape is a paid services that allow you to get more
            out of your experience with Artconomy. It sharply reduces your fees
            for Artconomy Shield, and allows you to track as many orders as you
            like.
          </p>
          <p>Landscape also comes with many extra features, like:</p>
          <ul>
            <li>Waitlisted orders</li>
            <li>Tipping after order completion</li>
            <li>Multi-stage orders</li>
            <li>PayPal invoicing for non-shield orders</li>
            <li>Access to the Landscape channel on our Discord</li>
            <li>
              First consideration for
              <router-link
                :to="{
                  name: 'BuyAndSell',
                  params: { question: 'virtual-table' },
                }"
              >
                Virtual Table Events.
              </router-link>
            </li>
          </ul>
          <router-link
            v-if="isRegistered"
            :to="{ name: 'Upgrade', params: { username: viewerName } }"
          >
            Click this link to change plans!
          </router-link>
          <p v-else>
            Click the Upgrade link in the sidebar after you're logged in to
            upgrade your account!
          </p>
        </v-card-text>
      </template>
    </ac-question>
    <ac-question>
      <template #title>
        How are fees calculated? What determines your pricing?
      </template>
      <template #default>
        <v-card-text>
          <h3>Calculating Fees</h3>
          <p>
            Fees differ depending on your
            <router-link
              :to="{
                name: 'BuyAndSell',
                params: { question: 'compare-and-contrast-plans' },
              }"
            >
              plan
            </router-link>
            and whether or not you're using
            <router-link
              :to="{ name: 'BuyAndSell', params: { question: 'shield' } }"
            >
              Shield
            </router-link>
            to protect your order.
          </p>
          <p>
            When listing your products, you set your take home amount. The
            customer will always see the final price up front, so if our fees
            change, or your plan changes to one that includes lower fees for
            your clients, your take home amount does not change.
          </p>
          <p>
            The price calculator is available on every order and every product--
            it will show you the full consequences of any price change on fees.
            It also includes a handy calculator that lets you estimate your
            hourly rate so you can determine if your price is high enough to
            compensate for your time.
          </p>
          <h3>A word on our pricing</h3>
          <p>
            Artconomy Shield is an escrow service. Escrow services are uncommon
            online, and Stripe, our payment processor, is capable of handling
            it, but isn't optimized for it.
            <a
              href="https://artconomy.com/blog/posts/2022/11/16/escrow-for-art-commissions/"
              target="_blank"
              rel="noopener"
              >We are firm believers in escrow</a
            >, which is why we offer it. However, it does result in Stripe's
            fees being higher for us-- including a $2 fee for every connected
            account we pay out to <strong>each month</strong> on top of the
            credit card fees.
          </p>
          <p>
            As a result, fees must always incorporate this cost. However,
            with Landscape, this $2 (and other upstream fees) are chiefly
            covered every month by the subscription fee, so shield costs are
            able to be reduced significantly. This is also why tips are only
            available to Landscape users.
          </p>
          <p>
            For non-shield orders, there are still costs with hosting and
            maintaining the service. We offer our free tier for small time
            artists trying to get started. On our basic plan, however, we do
            charge a fee to offset costs on each non-shield order. We believe
            the order handling is the best out there for art commissions, and
            that the time saved will always be worth more than the fee. The net
            we receive for non-shield orders on our basic plan is calculated
            to be $1 after Stripe's processing fees.
          </p>
          <p>
            Our goal, then, is to try to make at least a dollar on each order,
            and always provide value worth the cost. With this 'at least $1 an
            order' target (preferably a bit more), we can easily project and
            guess how many orders we need to process to cover our costs and pay
            our team members.
          </p>
          <p>
            Why lay all this out, you may ask? Because Artconomy's goal is to
            help artists run their business, and that means helping them reason
            about pricing. The best way to do this is to lead by example,
            showing you how we structure things. If you'd like to be engaged
            deeply, in real time, with our decision making process, we encourage
            you to
            <a href="https://discord.gg/4nWK9mf">join our Discord server</a>,
            where you can learn more in the <code>#business-tips</code> channel.
            You can also read our
            <a
              href="https://artconomy.com/blog/posts/2020/04/29/7-tips-on-pricing-your-artwork/"
              rel="noopener"
              target="_blank"
              >tips on pricing your artwork.</a
            >
          </p>
        </v-card-text>
      </template>
    </ac-question>
    <ac-question>
      <template #title> What is the Artconomy Virtual Table? </template>
      <template #default>
        <v-card-text>
          <p>
            The Artconomy Virtual Table is an in-person/online hybrid experience
            run by Artconomy staffers at conventions. During a virtual table
            event, selected artists are on standby to take commission orders
            (often, con badges), which are printed on a printer and handed over
            during the convention. This way, you get the benefit of taking
            orders at a convention without having to leave home!
          </p>
          <v-img
            :src="conBadge"
            :contain="true"
            max-height="40vh"
            alt="An example convention badge printed and laminated on site."
          />
          <p>
            The Virtual Table is also an opportunity to sell your merch for
            events that you cannot physically attend. If you can get the
            merchandise to us ahead of the event and we have room, we'll sell it
            for you.
          </p>
          <p>
            The virtual table event is also quite social-- you'll be in a
            private Discord channel with other selected artists. Our artists
            typically stream together as they complete orders. If the pieces are
            safe for work (or the convention allows adult content) we'll stream
            the live drawing on a TV set right at our table!
          </p>
          <p>
            <strong>Virtual Table positions are limited--</strong> both based on
            how many events we have a booth at per year, and how many artists we
            can accommodate at a time during the event. Priority always goes to
            <router-link
              :to="{ name: 'BuyAndSell', params: { question: 'landscape' } }"
            >
              Landscape subscribers.
            </router-link>
            Service fee pricing depends on the event.
          </p>
          <p>
            If you're interested in joining a virtual table event,
            <a href="https://discord.gg/4nWK9mf">join our Discord</a> or
            <a href="https://twitter.com/ArtconomyArt/">follow us on Twitter</a
            >. for announcements.
          </p>
        </v-card-text>
      </template>
    </ac-question>
    <ac-question>
      <template #title>
        What banks can be linked to Artconomy Shield? What are the supported
        countries?
      </template>
      <template #default>
        <v-card-text>
          <p>
            Many countries are supported and their banks can be linked to use
            <router-link
              :to="{ name: 'BuyAndSell', params: { question: 'shield' } }"
            >
              Artconomy Shield.
            </router-link>
            When new countries are available from our processor, this list will
            be updated. However, Artconomy Shield is not required to list
            products and take orders on Artconomy. If your country is not yet
            supported, you can still take orders without Shield protection.
          </p>
          <p>
            The following countries are currently supported for shield
            protection:
          </p>
          <ac-load-section :controller="stripeCountries">
            <ul>
              <li
                v-for="country in stripeCountries.x!.countries"
                :key="country.value"
              >
                {{ country.title }}
              </li>
            </ul>
          </ac-load-section>
          <p>
            <strong>NOTE:</strong> This list is authoritative for shield. While
            Stripe's site says they do not support some of the above countries,
            that's only half-true: They support many more countries for payout
            than they do for fully featured platform accounts.
            <strong
              >The site's onboarding will guide you through the creation of an
              'Express' payout account with Stripe-- you do not need to sign up
              directly on their website.</strong
            >
          </p>
        </v-card-text>
      </template>
    </ac-question>
    <ac-question>
      <template #title>
        How does Artconomy help me manage my workload?
      </template>
      <template #default>
        <v-card-text>
          <p>
            Artconomy understand the problems artists have with managing their
            workload and communicating with commissioners. That's why we created
            Artconomy's workload management system, nicknamed
            <strong
              >"AWOO" (Artconomy Workflow Organization and Overview).</strong
            >
          </p>
          <h3>Getting an Overview</h3>
          <p>
            AWOO's features start basic-- the
            <router-link
              v-if="isRegistered"
              :to="{ name: 'Sales', params: { username: viewerName } }"
            >
              Sales
            </router-link>
            <span v-else>'Sales'</span>
            button in your sidebar will take you to the Workload panel, which
            shows all of your orders. Any with new activity are highlighted, and
            you can message all of your commissioners at any time with the
            'Broadcast to Buyers' button. That will add a comment on all of your
            orders for you.
          </p>
          <p>
            <strong
              >All orders offer a direct communication line with your
              commissioner.</strong
            >
            Commenting on an order sends an email alert and notification to the
            commissioner for them to review. This ensures that you do not have
            to keep individual track of customers' email addresses to get a hold
            of them, and you never have to write a journal entry with the
            subject 'if I owe you art, message me.' Feel free to comment and ask
            questions to make sure you can give your customers the best
            experience possible!
          </p>
          <p>
            You can also use the green
            <router-link
              :to="{ name: 'BuyAndSell', params: { question: 'invoicing' } }"
            >
              'New Invoice'
            </router-link>
            button to invoice out to a client rather than having them place an
            order.
          </p>
          <h3>Smart Availability</h3>
          <p>
            AWOO is also able to intelligently manage your availability. It
            begins with your
            <router-link
              v-if="isRegistered"
              :to="{ name: 'BuyAndSell', params: { questions: 'options' } }"
            >
              Slots, configurable in your settings.
            </router-link>
            <span v-else> Slots, configurable in your settings. </span>
            Your slots are the number of open spaces you have for commissions.
            Most commissions should take up one slot, but if you offer a product
            that takes more time, you can change the number of slots it takes
            up. For instance, if you have 10 slots, and sell inked pieces that
            take up 2 slots each, Artconomy will close commissions once you have
            five of them.
          </p>
          <p>
            AWOO is able to track multiple products' slots. If you set your
            slots to 10, and sell full color pieces that take up five slots, you
            could have one full color commission and two inked pieces (totalling
            9 points) leaving you with one point remaining. If you don't have
            any products that take up only one point, AWOO will close
            commissions for you.
          </p>
          <p>
            In addition to this, you may also specify the 'Max at Once' setting
            for a product. If you never want to do more than two sketches at a
            time, you would set this to 2 for your sketch product. This will
            make sure that if you already have two sketches accepted, AWOO will
            delist sketches from your store so you don't receive more requests
            for them.
          </p>
          <p>
            AWOO manages when you are considered 'open' for commissions, sending
            real-time alerts to watchers when you are available. Note that you
            may still be closed for commissions even if you have some workload
            to spare. See
            <router-link
              :to="{
                name: 'BuyAndSell',
                params: { question: 'why-commissions-disabled' },
              }"
            >
              'Why are my Commissions Disabled?'
            </router-link>
            for more information as to why this may happen.
          </p>
          <p>
            You can effectively disable AWOO's slot management by setting your
            Slot count to a number so high you'll never reach it. You can then
            open and close yourself with the
            <router-link
              v-if="isRegistered"
              :to="{
                name: 'Settings',
                params: { username: viewer!.username, tabName: 'options' },
              }"
            >
              Commissions Closed setting.
            </router-link>
            <span v-else>
              Commissions Closed setting, available on your settings page.
            </span>
            <strong
              >This is not recommended unless you are experienced in managing
              your workload.</strong
            >
            Appearing to be open when you are not leads to customer service
            issues, which can affect your rating and reputation. Alternatively,
            you can use the
            <router-link
              :to="{ name: 'BuyAndSell', params: { question: 'waitlists' } }"
            >
              Waitlist feature.
            </router-link>
          </p>
        </v-card-text>
      </template>
    </ac-question>
    <ac-question>
      <template #title>
        How can I invoice customers, or track orders not made on the site?
      </template>
      <template #default>
        <v-card-text>
          <iframe
            :width="videoWidth"
            :height="videoHeight"
            src="https://www.youtube-nocookie.com/embed/MMTyxXjN1ko?si=f9DKB3mr4TfregSw"
            title="YouTube video player"
            allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
            allowfullscreen
          />
          <p>
            If you're out and about at a convention, working on a special
            project, or you're taking orders on the fly from customers in your
            stream, you might want to create an order for tracking yourself,
            instead of having a customer do it.
            <router-link
              :to="{
                name: 'BuyAndSell',
                params: { question: 'workload-management' },
              }"
            >
              AWOO
            </router-link>
            can help you keep track of these orders. You can create a new
            invoice from your
            <router-link
              v-if="isRegistered && viewer!.artist_mode"
              :to="{ name: 'Sales', params: { username: viewer!.username } }"
            >
              sales page
            </router-link>
            <span v-else>sales page</span>. Just click the green button in the
            lower right to get started!
          </p>
          <p>Invoices can do several neat things. For instance:</p>
          <ul>
            <li>
              You can specify an email or Artconomy user name to send the
              invoice to in order to collect payment.
            </li>
            <li>
              You can use your existing product listings as a template for
              pricing and workload management.
            </li>
            <li>
              You can handle tasks that have already been paid, but which impact
              your workload, so AWOO can keep track of them.
            </li>
            <li>
              You can issue a completely custom order not related to any product
              you currently have listed.
            </li>
            <li>
              You can create an order that doesn't have the customer's
              information-- useful if you want to track the impact of an outside
              project or commission but don't need to send updates to anyone. In
              this case, just leave the customer email/username field blank.
            </li>
          </ul>
          <p>
            Invoices can always be issued, regardless of whether or not your
            commissions are closed, or a product is normally unavailable.
            <strong
              >Please be cautious when taking orders this way if you already
              have a full workload--</strong
            >
            failing to deliver pieces in a timely manner can affect your
            reputation, and it is better to keep promises you have already made
            than to make new ones.
          </p>
        </v-card-text>
      </template>
    </ac-question>
    <ac-question>
      <template #title> How does waitlisting work? </template>
      <template #default>
        <v-card-text>
          <p>
            Waitlists allow you to take orders that you aren't committing to
            complete. There are a few times when you might use waitlisting:
          </p>
          <ul>
            <li>
              You want to gauge interest in a commission type by letting people
              pre-order it.
            </li>
            <li>
              You're fully booked, but you want to keep track of interest for
              clients who are waiting.
            </li>
            <li>
              You have a
              <a
                href="https://www.findlaw.com/legalblogs/small-business/top-5-tips-to-keep-raffles-contests-legal/#section-1-2-no-purchase-necessary"
              >
                no-entry-cost raffle</a
              >
              where customers enter commission information.
            </li>
          </ul>
          <p>
            Wailists are currently only available to Landscape subscribers.
            Waitlisted orders have no commitment on the part of the artist--
            they don't have to be taken in any particular order and they don't
            have to be completed at all. You can also clear your waitlist at any
            time.
          </p>
          <p>
            You can either enable waitlist on a particular product, or you can
            waitlist orders as they come in. If a new order arrives and you wish
            to waitlist it, click the waitlist button at the top of the order.
          </p>
        </v-card-text>
      </template>
    </ac-question>
    <ac-question>
      <template #title> Why are my commissions disabled? </template>
      <template #default>
        <v-card-text>
          <p>
            <router-link
              :to="{
                name: 'BuyAndSell',
                params: { question: 'workload-management' },
              }"
            >
              AWOO
            </router-link>
            uses a smart algorithm to help determine if you should be considered
            open for commissions. On your sales page, you will see information
            about your current commission status and any reasons why you may not
            be open. Some of these reasons may include:
          </p>
          <ul>
            <li>
              You have marked yourself as 'commissions closed' in your settings.
            </li>
            <li>
              You have used up all of your slots, also configurable in your
              settings.
            </li>
            <li>
              You still have some slots, but none of your products will fit in
              the remaining workload.
            </li>
            <li>
              You still have some slots, but any products which DO fit in the
              remaining ones have already reached their 'max at once' limit.
            </li>
            <li>You may have an invoice with us which is past due.</li>
          </ul>
        </v-card-text>
      </template>
    </ac-question>
    <ac-question>
      <template #title> What is redaction? </template>
      <template #default>
        <v-card-text>
          <p>
            Artconomy believes in giving you tools to enhance your privacy and
            the privacy of your commissioners. Redaction purges nearly all
            details of an order, reducing the data footprint left behind after a
            commission.
          </p>
          <p>
            Artists may redact orders after enough time has passed for
            Artconomy's legal/contractual obligations to hold them has passed.
            For unshielded orders, this is immediately after an order is
            completed.
          </p>
          <p>
            For shielded orders, this is after any relevant chargeback windows
            have passed. Artconomy fights chargebacks on your behalf so you
            don't have to. To mount a defence, we retain order details as
            needed. Once the chargeback window has passed, old orders may be
            redacted.
          </p>
          <p>
            Content such as the comments, the references, the revisions, the
            linked characters, the title, and the requested details by the
            commissioner are cleared.
          </p>
          <p>
            Some data on an order can not be redacted as it may be required for
            tax/legal/financial requirement purposes, such as invoices and their
            line items, financial ledger entries, the buyer and seller, the link
            to the product invoiced, and the copy of your terms of service at
            the time of sale. If a submission has been created from an order,
            that submission will remain.
          </p>
          <p>
            The redaction functionality appears once a commission is in a closed
            state. Simply visit your deliverable and follow the instructions. If
            redaction is not yet available, but will be, the details on when to
            expect the redaction to be available will be at the top of the
            order.
          </p>
          <p>
            Artconomy expects to provide auto-redaction functionality in a
            future release.
          </p>
        </v-card-text>
      </template>
    </ac-question>
    <ac-question>
      <template #title> Can I use PayPal? </template>
      <template #default>
        <v-card-text>
          <p>
            <strong>You can!</strong> You can track an order and handle its
            payment off-site with PayPal. If you have a
            <router-link
              :to="{ name: 'BuyAndSell', params: { question: 'Landscape' } }"
            >
              Landscape subscription,
            </router-link>
            Artconomy can generate
            <router-link
              :to="{ name: 'BuyAndSell', params: { question: 'Landscape' } }"
            >
              invoices on PayPal for you,
            </router-link>
            and add orders to your queue once those invoices are paid. However,
            you might want to consider using
            <router-link
              :to="{ name: 'BuyAndSell', params: { question: 'shield' } }"
            >
              Artconomy Shield
            </router-link>
            instead.
          </p>
          <p>PayPal has several key limitations:</p>
          <ul>
            <li>
              PayPal has separate policies for business and personal use that
              can be confusing.
            </li>
            <li>
              PayPal's dispute resolution is limited and not well suited for
              art, especially when using their personal service.
            </li>
            <li>
              PayPal has been known to suspend accounts with little recourse or
              comment.
            </li>
            <li>
              PayPal has a mixed reputation when dealing with adult content.
              Their written policy, taken literally, bans all adult content,
              though many still use it for the purpose.
            </li>
          </ul>
          <p>
            For these reasons, we recommend using
            <router-link
              :to="{ name: 'BuyAndSell', params: { question: 'shield' } }"
            >
              Artconomy Shield
            </router-link>
            to protect your orders.
          </p>
          <p>
            However, if you need to use PayPal, such as if Shield is not
            supported in your country or you need invoicing features Artconomy
            does not yet support, you can integrate Artconomy and PayPal
            together. Setup for PayPal integration is in your
            <router-link
              :to="{ name: 'MyView', params: { viewName: 'Premium' } }"
            >
              Premium Settings.
            </router-link>
          </p>
        </v-card-text>
      </template>
    </ac-question>
    <ac-question>
      <template #title> How does Artconomy compare to Patreon? </template>
      <template #default>
        <v-card-text>
          <p>
            Patreon is a popular platform for artists that allows them to
            receive monthly contributions from patrons. Patrons are also able to
            receive exclusive rewards for being monthly donors.
          </p>
          <p>
            We believe that services like Patreon and Artconomy are best used
            together to help artists achieve their goals of self-sufficiency
            from their artistic work.
          </p>
          <p>
            Patreon has a significant limitation however--
            <a
              href="https://en.wikipedia.org/wiki/Free-rider_problem"
              target="_blank"
              >the free rider problem.</a
            >
            The more patrons one has, the more likely it is that one will
            distribute the rewards to people who are not contributing. This
            disincentivizes people from signing up for an artist's Patreon, as
            they can get the art for free.
          </p>
          <p>
            While solutions exist to deter this behavior-- such as sending
            takedown notices to hosting sites and threatening legal action,
            these often create customer relations issues and cost more time and
            effort than can be recovered, and can never be fully effective, as
            people may always share files privately. Additionally, offering
            physical goods and other creative uncopyable rewards is an option,
            but may not always be practical.
          </p>
          <p>
            Artconomy does not have this problem, as each commission is tied to
            a specific seller who pays individually for their pieces. Thankfully
            one does not need to exclusively use Patreon or Artconomy.
          </p>
          <p>
            Artconomy may add functionality like Patreon has in the future, but
            for now remains focused on building the best freelance art business
            toolkit.
          </p>
        </v-card-text>
      </template>
    </ac-question>
    <ac-question>
      <template #title> What are Featured Products? </template>
      <template #default>
        <v-card-text>
          <p>
            Featured products are products hand-curated by Artconomy staff.
            Several criteria are used to determine whether a product is
            featured,
            <em>some of which are subjective and up to staff judgement.</em>
            These include (but are not limited to):
          </p>
          <ul>
            <li>Quality of the work Offered</li>
            <li>
              Ratings and feedback from commissioners who have worked with the
              artist
            </li>
            <li>Value for price</li>
            <li>Shield Capability (Not required, but it helps!)</li>
          </ul>
          <p>
            Featured products may change and are rotated on the front page at
            random. If you believe there is a product that should be considered
            for featured status,
            <a href="#" @click.prevent="store.commit('supportDialog', true)"
              >please contact support</a
            >.
          </p>
        </v-card-text>
      </template>
    </ac-question>
    <ac-question>
      <template #title> Is Artconomy Secure? </template>
      <template #default>
        <v-card-text>
          <p>
            No system is completely secure, and anyone who advises you otherwise
            should be regarded with suspicion, or at least considered ignorant.
          </p>
          <p>
            However, Artconomy takes security seriously. We do not allow
            unencrypted connections to our site. Payments are processed through
            Stripe, with card data sent directly to their servers rather than
            ours. If someone were to hack in to our servers, they would not be
            able to retrieve your card number.
          </p>
          <p>
            Passwords are not stored in plain text, but are hashed to prevent
            release of your raw password. They are also salted to reduce the
            probability of hackers finding a password that works with the
            resulting hash and using it to log into other services.
          </p>
          <p>
            Artconomy also uses strict frameworks for accessing and manipulating
            its databases to reduce the probability of SQL injections and makes
            use of anti-clickjacking technology.
          </p>
          <p>
            For especially sensitive data that must be stored on our servers, we
            use encryption with offline, cold stored, secured keys, which are
            used only as long as explicit operations by our executive technical
            staff require.
            <strong
              >Note: At the time of writing, no data of this nature is actually
              stored on Artconomy, but if we end up having to store some, we
              will do so in this manner.</strong
            >
          </p>
          <p>
            These are only some of the things we do to keep your data safe, and
            we continue to keep security in mind when developing our products.
            You are always advised to use
            <router-link
              v-if="isRegistered"
              :to="{
                name: 'Settings',
                params: {
                  username: viewer!.username,
                  tabName: 'credentials',
                  subTabName: 'two-factor',
                },
              }"
            >
              Two-factor authentication, configurable in your settings,
            </router-link>
            <span v-else>
              Two-factor authentication, configurable in your settings,
            </span>
            for extra security, Especially if you are an artist!
          </p>
          <p>
            Do not share your account password with anyone. Artconomy staff will
            <em><strong>never</strong></em>
            ask for your password.
          </p>
        </v-card-text>
      </template>
    </ac-question>
    <ac-question>
      <template #title> How do I get paid? </template>
      <template #default>
        <v-card-text>
          <p>
            After you have completed your tasks, the money you've earned will be
            released to your Artconomy account holdings. It will automatically
            be sent to your bank account, unless you have opted out of auto
            withdraw, in which case
            <router-link
              v-if="isRegistered"
              :to="{
                name: 'Settings',
                params: {
                  username: viewer!.username,
                  tabName: 'payment',
                  subTabName: 'disbursement',
                },
              }"
            >
              you may submit a withdrawal request.
            </router-link>
            <span v-else> you may submit a withdrawal request. </span>
            Payouts take up to 5 business days to complete, but usually complete
            in 2-3. If you're having an issue with your payout,
            <a href="#" @click.prevent="store.commit('supportDialog', true)"
              >please contact support!</a
            >
          </p>
        </v-card-text>
      </template>
    </ac-question>
    <ac-question>
      <template #title>
        Does Artconomy Support Cryptocurrency Payments?
      </template>
      <template #default>
        <v-card-text>
          <p>
            Not at this time. However we are looking to implement support for
            Monero and potentially other cryptocurrencies in the future.
          </p>
        </v-card-text>
      </template>
    </ac-question>
    <ac-question>
      <template #title> Does Artconomy Support Auctions? </template>
      <template #default>
        <v-card-text>
          <p>
            Artconomy does not presently support auctions but intends to do so
            in the future.
          </p>
        </v-card-text>
      </template>
    </ac-question>
    <ac-question>
      <template #title>
        Does Artconomy Support the Sale of Physical Goods?
      </template>
      <template #default>
        <v-card-text>
          <p>
            Artconomy does not presently support the sale of physical goods
            <strong
              >aside from original pieces made during the commissioning
              process--</strong
            >
            it does not have an inventory system. When shipping physically
            commissioned goods while using Artconomy Shield, you must buy
            insurance to cover the price of any shipment you make, including the
            commission price, and you must incorporate the shipping price into
            the final sale price.
          </p>
          <p>
            We recommend asking the customer for their address before accepting
            the order so you can precalculate these shipping costs.
          </p>
        </v-card-text>
      </template>
    </ac-question>
    <ac-question>
      <template #title>
        Does Artconomy handle digital download sales?
      </template>
      <template #default>
        <v-card-text>
          <p>
            Artconomy is set up for custom art commissions, and those custom art
            commissions are usually digital in nature. However it is not built
            for goods like premade digital download packs. Such functionality
            may be available in the future.
          </p>
        </v-card-text>
      </template>
    </ac-question>
  </v-expansion-panels>
</template>

<script setup lang="ts">
import { BASE_URL } from "@/lib/lib.ts"
import { useQuestionSet } from "@/components/views/faq/mixins/question-set.ts"
import { useSingle } from "@/store/singles/hooks.ts"
import { useRouter } from "vue-router"
import { useForm } from "@/store/forms/hooks.ts"
import { useViewer } from "@/mixins/viewer.ts"
import { useStore } from "vuex"
import { ArtState } from "@/store/artState.ts"
import AcQuestion from "@/components/views/faq/AcQuestion.vue"
import { mdiShieldHalfFull } from "@mdi/js"
import { defineAsyncComponent, computed } from "vue"
import type { StripeCountryList } from "@/types/main"
import { useDisplay } from "vuetify"
const AcLoadSection = defineAsyncComponent(
  () => import("@/components/wrappers/AcLoadSection.vue"),
)

const router = useRouter()
const { isRegistered, viewer, viewerName } = useViewer()
const store = useStore<ArtState>()

const { tab } = useQuestionSet([
  "how-to-buy",
  "how-to-sell",
  "shield",
  "disputes",
  "compare-and-contrast-plans",
  "landscape",
  "fee-calculation",
  "virtual-table",
  "bank-accounts",
  "workload-management",
  "invoicing",
  "waitlists",
  "why-commissions-disabled",
  "what-is-redaction",
  "paypal",
  "patreon-comparison",
  "featured-products",
  "security",
  "payouts",
  "crypto-currencies",
  "auctions",
  "physical-goods",
  "digital-downloads",
])

const conBadge = new URL("/static/images/con-badge.jpg", BASE_URL).href
const stripeCountries = useSingle<StripeCountryList>("stripeCountries")
const searchForm = useForm("search")

const searchOpen = () => {
  searchForm.reset()
  router.push({ name: "SearchProducts" })
}
const display = useDisplay()

const videoWidth = computed(() => {
  if (display.width.value * 0.8 < 560) {
    return Math.round(display.width.value * 0.8)
  }
  return 560
})
const videoHeight = computed(() => {
  return Math.round(videoWidth.value / (16 / 9))
})
</script>
